from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.schemas import SessionCreate, SessionResponse
from models.database import Session as DBSession
from config.database import get_db

router = APIRouter()

@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(db: Session = Depends(get_db)):
    """
    Get all analysis sessions
    """
    try:
        sessions = db.query(DBSession).order_by(DBSession.created_at.desc()).all()
        return [
            SessionResponse(
                id=session.id,
                product_idea=session.product_idea,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at
            )
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """
    Create a new analysis session
    """
    try:
        db_session = DBSession(
            product_idea=session_data.product_idea,
            status="created"
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        return SessionResponse(
            id=db_session.id,
            product_idea=db_session.product_idea,
            status=db_session.status,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """
    Get a specific analysis session
    """
    try:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            id=session.id,
            product_idea=session.product_idea,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """
    Delete an analysis session
    """
    try:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        db.delete(session)
        db.commit()
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
