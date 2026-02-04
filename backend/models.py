"""
SQLAlchemy ORM models for the RSVP system.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class Player(Base):
    """
    Player model representing a person who can RSVP for a game.
    
    States:
    - rsvp_status: "IN" or "OUT"
    - waitlist_position: None if in main 22, otherwise 1, 2, 3... for waitlist order
    - paid: Must be True before check-in is allowed
    - checked_in: True after successful game-day check-in
    """
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    
    # RSVP status: "IN" or "OUT"
    rsvp_status = Column(String(10), default="OUT", nullable=False)
    
    # Timestamp when RSVP was submitted (for waitlist ordering)
    rsvp_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Waitlist position: None = confirmed IN (within 22), 1+ = waitlist position
    waitlist_position = Column(Integer, nullable=True, default=None)
    
    # Payment status
    paid = Column(Boolean, default=False, nullable=False)
    
    # Check-in status (game day)
    checked_in = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.name}', status={self.rsvp_status}, waitlist={self.waitlist_position})>"
    
    @property
    def is_confirmed(self):
        """Player is IN and not on waitlist"""
        return self.rsvp_status == "IN" and self.waitlist_position is None
    
    @property
    def is_waitlisted(self):
        """Player is IN but on waitlist"""
        return self.rsvp_status == "IN" and self.waitlist_position is not None
