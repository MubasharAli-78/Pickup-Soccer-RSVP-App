"""
RSVP Service - Core business logic for RSVP operations.
Handles IN/OUT voting with 22-player limit and waitlist management.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Player

# Maximum players allowed in the confirmed list
MAX_CONFIRMED_PLAYERS = 22


def get_confirmed_count(db: Session) -> int:
    """Count players who are IN and NOT on waitlist"""
    return db.query(Player).filter(
        Player.rsvp_status == "IN",
        Player.waitlist_position.is_(None)
    ).count()


def get_next_waitlist_position(db: Session) -> int:
    """Get the next available waitlist position"""
    max_pos = db.query(func.max(Player.waitlist_position)).scalar()
    return (max_pos or 0) + 1


def get_player_by_name(db: Session, name: str) -> Player | None:
    """Find a player by name (case-insensitive)"""
    return db.query(Player).filter(
        func.lower(Player.name) == func.lower(name)
    ).first()


def get_player_by_id(db: Session, player_id: int) -> Player | None:
    """Find a player by ID"""
    return db.query(Player).filter(Player.id == player_id).first()


def rsvp_in(db: Session, player_name: str) -> tuple[Player, str]:
    """
    RSVP a player IN.
    
    Rules:
    - If under 22 confirmed players: add to confirmed list
    - If 22+ confirmed players: add to waitlist with timestamp-based position
    
    Returns:
        tuple: (Player object, status message)
    """
    timestamp = datetime.now(timezone.utc)
    
    # Check if player already exists
    player = get_player_by_name(db, player_name)
    
    if player:
        # Player exists - update their status
        if player.rsvp_status == "IN":
            if player.waitlist_position is None:
                return player, "Already confirmed IN"
            else:
                return player, f"Already on waitlist at position {player.waitlist_position}"
        
        # Player was OUT, now going IN
        player.rsvp_status = "IN"
        player.rsvp_timestamp = timestamp
        player.paid = False
        player.checked_in = False
        
    else:
        # Create new player
        player = Player(
            name=player_name.strip(),
            rsvp_status="IN",
            rsvp_timestamp=timestamp,
            paid=False,
            checked_in=False
        )
        db.add(player)
    
    # Determine if confirmed or waitlisted
    confirmed_count = get_confirmed_count(db)
    
    if confirmed_count < MAX_CONFIRMED_PLAYERS:
        player.waitlist_position = None
        message = f"Confirmed IN! ({confirmed_count + 1}/{MAX_CONFIRMED_PLAYERS} spots filled)"
    else:
        player.waitlist_position = get_next_waitlist_position(db)
        message = f"Added to waitlist at position {player.waitlist_position}"
    
    db.commit()
    db.refresh(player)
    
    return player, message


def rsvp_out(db: Session, player_name: str) -> tuple[Player | None, str]:
    """
    RSVP a player OUT.
    
    Rules:
    - Set status to OUT
    - Clear waitlist position
    - If player was confirmed, promote next waitlisted player
    
    Returns:
        tuple: (Player object or None, status message)
    """
    player = get_player_by_name(db, player_name)
    
    if not player:
        # Create new player as OUT
        player = Player(
            name=player_name.strip(),
            rsvp_status="OUT",
            rsvp_timestamp=datetime.now(timezone.utc),
            paid=False,
            checked_in=False,
            waitlist_position=None
        )
        db.add(player)
        db.commit()
        db.refresh(player)
        return player, "Marked as OUT"
    
    was_confirmed = player.is_confirmed
    
    # Update player status
    player.rsvp_status = "OUT"
    player.waitlist_position = None
    player.paid = False
    player.checked_in = False
    
    db.commit()
    
    # If player was confirmed, promote from waitlist
    if was_confirmed:
        promoted = promote_from_waitlist(db)
        if promoted:
            db.refresh(player)
            return player, f"Marked as OUT. {promoted.name} promoted from waitlist!"
    
    db.refresh(player)
    return player, "Marked as OUT"


def promote_from_waitlist(db: Session) -> Player | None:
    """
    Promote the first player from waitlist to confirmed.
    Called when a confirmed player goes OUT.
    
    Returns:
        Player: The promoted player, or None if waitlist is empty
    """
    # Get the player with the lowest waitlist position
    next_player = db.query(Player).filter(
        Player.rsvp_status == "IN",
        Player.waitlist_position.isnot(None)
    ).order_by(Player.waitlist_position.asc()).first()
    
    if next_player:
        next_player.waitlist_position = None
        db.commit()
        
        # Recalculate waitlist positions
        recalculate_waitlist_positions(db)
        
        db.refresh(next_player)
        return next_player
    
    return None


def recalculate_waitlist_positions(db: Session):
    """
    Recalculate waitlist positions after a promotion.
    Ensures positions are sequential: 1, 2, 3...
    """
    waitlisted = db.query(Player).filter(
        Player.rsvp_status == "IN",
        Player.waitlist_position.isnot(None)
    ).order_by(Player.rsvp_timestamp.asc()).all()
    
    for i, player in enumerate(waitlisted, start=1):
        player.waitlist_position = i
    
    db.commit()


def get_all_players_categorized(db: Session) -> dict:
    """
    Get all players categorized by status.
    
    Returns:
        dict with confirmed, waitlist, and out lists
    """
    confirmed = db.query(Player).filter(
        Player.rsvp_status == "IN",
        Player.waitlist_position.is_(None)
    ).order_by(Player.rsvp_timestamp.asc()).all()
    
    waitlist = db.query(Player).filter(
        Player.rsvp_status == "IN",
        Player.waitlist_position.isnot(None)
    ).order_by(Player.waitlist_position.asc()).all()
    
    out = db.query(Player).filter(
        Player.rsvp_status == "OUT"
    ).order_by(Player.name.asc()).all()
    
    return {
        "confirmed": confirmed,
        "waitlist": waitlist,
        "out": out,
        "total_confirmed": len(confirmed),
        "total_waitlist": len(waitlist),
        "spots_available": max(0, MAX_CONFIRMED_PLAYERS - len(confirmed))
    }
