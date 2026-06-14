from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/")
def list_sessions(db: Session = Depends(get_db)):
    """Return all brew sessions."""
    sessions = db.query(models.BrewSession).all()
    return sessions


@router.get("/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Return a single brew session by ID."""
    session = db.query(models.BrewSession).filter(models.BrewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Brew session not found")
    return session


@router.post("/")
def create_session(db: Session = Depends(get_db)):
    """Create a new brew session. (Week 3)"""
    return {"message": "Session creation coming in Week 3"}


@router.post("/{session_id}/readings")
def add_fermentation_reading(session_id: int, db: Session = Depends(get_db)):
    """Manually add a fermentation reading. (Week 4)"""
    return {"message": "Manual readings coming in Week 4"}


@router.post("/rapt/webhook")
def rapt_webhook(db: Session = Depends(get_db)):
    """Receive data from the RAPT Pill via webhook. (Week 4)"""
    return {"message": "RAPT webhook coming in Week 4"}
