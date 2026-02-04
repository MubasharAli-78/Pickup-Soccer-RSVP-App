"""
Export Service - CSV export functionality.
Exports all player data with timestamps for record keeping.
"""

import io
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from models import Player


def export_players_to_csv(db: Session) -> str:
    """
    Export all players to CSV format.
    
    Includes:
    - Player name
    - RSVP status
    - RSVP timestamp
    - Waitlist position
    - Payment status
    - Check-in status
    
    Returns:
        str: CSV content as string
    """
    # Query all players
    players = db.query(Player).order_by(
        Player.rsvp_status.desc(),  # IN first, then OUT
        Player.waitlist_position.asc().nullsfirst(),  # Confirmed first, then waitlist
        Player.rsvp_timestamp.asc()  # Then by timestamp
    ).all()
    
    # Convert to list of dictionaries
    data = []
    for player in players:
        # Determine display status
        if player.rsvp_status == "OUT":
            display_status = "OUT"
        elif player.waitlist_position is None:
            display_status = "CONFIRMED"
        else:
            display_status = f"WAITLIST #{player.waitlist_position}"
        
        data.append({
            "ID": player.id,
            "Name": player.name,
            "RSVP Status": player.rsvp_status,
            "Display Status": display_status,
            "RSVP Timestamp": player.rsvp_timestamp.strftime("%Y-%m-%d %H:%M:%S") if player.rsvp_timestamp else "",
            "Waitlist Position": player.waitlist_position if player.waitlist_position else "",
            "Paid": "YES" if player.paid else "NO",
            "Checked In": "YES" if player.checked_in else "NO"
        })
    
    # Create DataFrame and convert to CSV
    df = pd.DataFrame(data)
    
    return df.to_csv(index=False)


def export_players_to_csv_bytes(db: Session) -> bytes:
    """
    Export players to CSV as bytes (for file download).
    
    Returns:
        bytes: CSV content as UTF-8 encoded bytes
    """
    csv_content = export_players_to_csv(db)
    return csv_content.encode('utf-8')


def get_export_filename() -> str:
    """
    Generate a filename for the CSV export.
    
    Returns:
        str: Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"rsvp_export_{timestamp}.csv"
