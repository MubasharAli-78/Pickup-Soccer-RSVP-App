"""
Pydantic schemas for request/response validation.
These define the API contract between frontend and backend.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


# ============== Request Schemas ==============

class RSVPRequest(BaseModel):
    """Request to RSVP a player IN or OUT"""
    name: str = Field(..., min_length=1, max_length=100, description="Player name")
    status: Literal["IN", "OUT"] = Field(..., description="RSVP status")


class PaymentRequest(BaseModel):
    """Request to update payment status"""
    paid: bool = Field(..., description="Payment status")


# ============== Response Schemas ==============

class PlayerResponse(BaseModel):
    """Response schema for a single player"""
    id: int
    name: str
    rsvp_status: str
    rsvp_timestamp: datetime
    waitlist_position: Optional[int]
    paid: bool
    checked_in: bool
    is_confirmed: bool
    is_waitlisted: bool

    class Config:
        from_attributes = True


class PlayerListResponse(BaseModel):
    """Response with categorized player lists"""
    confirmed: list[PlayerResponse] = Field(default_factory=list, description="Players confirmed IN (max 22)")
    waitlist: list[PlayerResponse] = Field(default_factory=list, description="Players on waitlist")
    out: list[PlayerResponse] = Field(default_factory=list, description="Players who RSVP'd OUT")
    total_confirmed: int = Field(default=0, description="Count of confirmed players")
    total_waitlist: int = Field(default=0, description="Count of waitlisted players")
    spots_available: int = Field(default=22, description="Spots still available")


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool
    message: str
    player: Optional[PlayerResponse] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
