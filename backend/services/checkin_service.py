"""
Check-in Service - Game day check-in logic.
Only allows check-in if player is confirmed IN AND has paid.
"""

from sqlalchemy.orm import Session
from models import Player
from services.rsvp_service import get_player_by_id


class CheckInError(Exception):
    """Custom exception for check-in validation failures"""
    pass


def check_in_player(db: Session, player_id: int) -> tuple[Player, str]:
    """
    Check in a player on game day.
    
    Rules:
    1. Player must exist
    2. Player must be RSVP'd IN
    3. Player must NOT be on waitlist (must be confirmed)
    4. Player must have PAID
    
    Returns:
        tuple: (Player object, success message)
        
    Raises:
        CheckInError: If any validation fails
    """
    player = get_player_by_id(db, player_id)
    
    if not player:
        raise CheckInError("Player not found")
    
    if player.rsvp_status != "IN":
        raise CheckInError(f"Player is not RSVP'd IN (current status: {player.rsvp_status})")
    
    if player.waitlist_position is not None:
        raise CheckInError(f"Player is on waitlist at position {player.waitlist_position}. Cannot check in from waitlist.")
    
    if not player.paid:
        raise CheckInError("Player must pay before checking in. Payment required!")
    
    if player.checked_in:
        return player, "Player is already checked in"
    
    # All validations passed - check in the player
    player.checked_in = True
    db.commit()
    db.refresh(player)
    
    return player, f"Successfully checked in {player.name}!"


def undo_check_in(db: Session, player_id: int) -> tuple[Player, str]:
    """
    Undo a player's check-in (admin function).
    
    Returns:
        tuple: (Player object, message)
    """
    player = get_player_by_id(db, player_id)
    
    if not player:
        raise CheckInError("Player not found")
    
    if not player.checked_in:
        return player, "Player was not checked in"
    
    player.checked_in = False
    db.commit()
    db.refresh(player)
    
    return player, f"Check-in undone for {player.name}"


def get_check_in_stats(db: Session) -> dict:
    """
    Get check-in statistics for game day.
    
    Returns:
        dict with check-in stats
    """
    from sqlalchemy import func
    
    total_confirmed = db.query(Player).filter(
        Player.rsvp_status == "IN",
        Player.waitlist_position.is_(None)
    ).count()
    
    total_paid = db.query(Player).filter(
        Player.rsvp_status == "IN",
        Player.waitlist_position.is_(None),
        Player.paid == True
    ).count()
    
    total_checked_in = db.query(Player).filter(
        Player.checked_in == True
    ).count()
    
    return {
        "total_confirmed": total_confirmed,
        "total_paid": total_paid,
        "total_checked_in": total_checked_in,
        "awaiting_payment": total_confirmed - total_paid,
        "awaiting_check_in": total_paid - total_checked_in
    }
