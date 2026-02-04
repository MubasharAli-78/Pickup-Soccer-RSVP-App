"""
Pickup Soccer RSVP & Check-in System
=====================================
FastAPI backend with all API endpoints.

Features:
- RSVP IN/OUT with 22-player limit
- Automatic waitlist management
- Payment tracking
- Game-day check-in (requires payment)
- CSV export with timestamps
"""

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Player
from schemas import (
    RSVPRequest, 
    PaymentRequest,
    PlayerResponse, 
    PlayerListResponse, 
    MessageResponse,
    ErrorResponse
)
from services import rsvp_service, checkin_service, export_service

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Pickup Soccer RSVP System",
    description="RSVP and Check-in system for pickup soccer games",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Pickup Soccer RSVP System is running!"}


# ============== Player Endpoints ==============

@app.get("/players", response_model=PlayerListResponse, tags=["Players"])
def get_all_players(db: Session = Depends(get_db)):
    """
    Get all players categorized by status.
    
    Returns confirmed players (max 22), waitlist, and OUT players.
    """
    result = rsvp_service.get_all_players_categorized(db)
    return PlayerListResponse(
        confirmed=[PlayerResponse.model_validate(p) for p in result["confirmed"]],
        waitlist=[PlayerResponse.model_validate(p) for p in result["waitlist"]],
        out=[PlayerResponse.model_validate(p) for p in result["out"]],
        total_confirmed=result["total_confirmed"],
        total_waitlist=result["total_waitlist"],
        spots_available=result["spots_available"]
    )


@app.get("/players/{player_id}", response_model=PlayerResponse, tags=["Players"])
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get a single player by ID"""
    player = rsvp_service.get_player_by_id(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerResponse.model_validate(player)


# ============== RSVP Endpoints ==============

@app.post("/players/rsvp", response_model=MessageResponse, tags=["RSVP"])
def rsvp_player(request: RSVPRequest, db: Session = Depends(get_db)):
    """
    RSVP a player IN or OUT.
    
    Rules:
    - First 22 players are confirmed IN
    - Additional players go to timestamp-ordered waitlist
    - Going OUT promotes next waitlisted player
    """
    try:
        if request.status == "IN":
            player, message = rsvp_service.rsvp_in(db, request.name)
        else:
            player, message = rsvp_service.rsvp_out(db, request.name)
        
        return MessageResponse(
            success=True,
            message=message,
            player=PlayerResponse.model_validate(player) if player else None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============== Payment Endpoints ==============

@app.put("/players/{player_id}/pay", response_model=MessageResponse, tags=["Payment"])
def mark_player_paid(player_id: int, request: PaymentRequest, db: Session = Depends(get_db)):
    """
    Mark a player as paid or unpaid.
    
    Payment is required before check-in on game day.
    """
    player = rsvp_service.get_player_by_id(db, player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if player.rsvp_status != "IN":
        raise HTTPException(status_code=400, detail="Can only mark payment for players who are IN")
    
    player.paid = request.paid
    db.commit()
    db.refresh(player)
    
    status = "paid" if request.paid else "unpaid"
    return MessageResponse(
        success=True,
        message=f"{player.name} marked as {status}",
        player=PlayerResponse.model_validate(player)
    )


# ============== Check-in Endpoints ==============

@app.put("/players/{player_id}/checkin", response_model=MessageResponse, tags=["Check-in"])
def check_in_player(player_id: int, db: Session = Depends(get_db)):
    """
    Check in a player on game day.
    
    Rules:
    - Player must be RSVP'd IN
    - Player must NOT be on waitlist
    - Player must have PAID
    """
    try:
        player, message = checkin_service.check_in_player(db, player_id)
        return MessageResponse(
            success=True,
            message=message,
            player=PlayerResponse.model_validate(player)
        )
    except checkin_service.CheckInError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/players/{player_id}/undo-checkin", response_model=MessageResponse, tags=["Check-in"])
def undo_check_in(player_id: int, db: Session = Depends(get_db)):
    """Undo a player's check-in (admin function)"""
    try:
        player, message = checkin_service.undo_check_in(db, player_id)
        return MessageResponse(
            success=True,
            message=message,
            player=PlayerResponse.model_validate(player)
        )
    except checkin_service.CheckInError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/checkin/stats", tags=["Check-in"])
def get_checkin_stats(db: Session = Depends(get_db)):
    """Get check-in statistics for game day"""
    return checkin_service.get_check_in_stats(db)


# ============== Export Endpoints ==============

@app.get("/export/csv", tags=["Export"])
def export_csv(db: Session = Depends(get_db)):
    """
    Export all players to CSV file.
    
    Includes timestamps, status, payment, and check-in information.
    """
    csv_bytes = export_service.export_players_to_csv_bytes(db)
    filename = export_service.get_export_filename()
    
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ============== Admin Endpoints ==============

@app.delete("/players/{player_id}", response_model=MessageResponse, tags=["Admin"])
def delete_player(player_id: int, db: Session = Depends(get_db)):
    """Delete a player completely (admin function)"""
    player = rsvp_service.get_player_by_id(db, player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    was_confirmed = player.is_confirmed
    player_name = player.name
    
    db.delete(player)
    db.commit()
    
    # Promote from waitlist if needed
    if was_confirmed:
        promoted = rsvp_service.promote_from_waitlist(db)
        if promoted:
            return MessageResponse(
                success=True,
                message=f"Deleted {player_name}. {promoted.name} promoted from waitlist!"
            )
    
    return MessageResponse(
        success=True,
        message=f"Deleted {player_name}"
    )


@app.post("/admin/reset", response_model=MessageResponse, tags=["Admin"])
def reset_all_data(db: Session = Depends(get_db)):
    """Reset all player data (admin function - use with caution!)"""
    db.query(Player).delete()
    db.commit()
    
    return MessageResponse(
        success=True,
        message="All player data has been reset"
    )


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
