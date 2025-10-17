from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from models.schemas import AnalysisRequest, AnalysisResponse
from services.analysis_service import AnalysisService
from config.database import get_db
from models.database import Session as DBSession, AnalysisResult
import json

router = APIRouter()
analysis_service = AnalysisService()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_product_idea(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = get_db()
):
    """
    Analyze a product idea and return market research results
    """
    try:
        # Create new session in database
        db_session = DBSession(
            product_idea=request.product_idea,
            status="processing"
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        # Run analysis in background
        background_tasks.add_task(
            run_analysis_background,
            request.product_idea,
            db_session.id,
            db
        )
        
        # Return immediate response
        return AnalysisResponse(
            session_id=db_session.id,
            product_idea=request.product_idea,
            analysis_results=None,  # Will be updated via WebSocket
            metadata={
                "processing_started": True,
                "session_id": db_session.id
            },
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis_background(product_idea: str, session_id: int, db: Session):
    """
    Background task to run analysis and save results
    """
    try:
        # Run the analysis
        analysis_response = await analysis_service.run_analysis(product_idea, session_id)
        
        # Save results to database
        save_analysis_results(db, session_id, analysis_response)
        
    except Exception as e:
        print(f"Background analysis error: {e}")
        # Update session status to failed
        db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if db_session:
            db_session.status = "failed"
            db.commit()

def save_analysis_results(db: Session, session_id: int, analysis_response: AnalysisResponse):
    """Save analysis results to database"""
    try:
        # Convert results to JSON strings for storage
        personas_json = json.dumps([persona.dict() for persona in analysis_response.analysis_results.personas])
        opinions_json = json.dumps([opinion.dict() for opinion in analysis_response.analysis_results.opinions])
        sentiment_json = json.dumps(analysis_response.analysis_results.sentiment_breakdown.dict())
        
        # Create analysis result record
        analysis_result = AnalysisResult(
            session_id=session_id,
            personas=personas_json,
            opinions=opinions_json,
            summary=analysis_response.analysis_results.summary,
            sentiment_breakdown=sentiment_json,
            market_potential=analysis_response.analysis_results.market_potential,
            confidence_score=analysis_response.metadata.get("confidence_score", 0)
        )
        
        db.add(analysis_result)
        
        # Update session status
        db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if db_session:
            db_session.status = "completed"
        
        db.commit()
        
    except Exception as e:
        print(f"Error saving analysis results: {e}")
        db.rollback()

@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_results(analysis_id: int, db: Session = get_db()):
    """
    Get analysis results by ID
    """
    try:
        # Get session
        db_session = db.query(DBSession).filter(DBSession.id == analysis_id).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get analysis results
        analysis_result = db.query(AnalysisResult).filter(AnalysisResult.session_id == analysis_id).first()
        
        if not analysis_result:
            return AnalysisResponse(
                session_id=analysis_id,
                product_idea=db_session.product_idea,
                analysis_results=None,
                metadata={"status": "processing"},
                status=db_session.status
            )
        
        # Parse JSON data
        personas = json.loads(analysis_result.personas) if analysis_result.personas else []
        opinions = json.loads(analysis_result.opinions) if analysis_result.opinions else []
        sentiment_breakdown = json.loads(analysis_result.sentiment_breakdown) if analysis_result.sentiment_breakdown else {}
        
        # Create response
        from models.schemas import AnalysisResults, Persona, Opinion, SentimentBreakdown
        
        analysis_results = AnalysisResults(
            personas=[Persona(**p) for p in personas],
            opinions=[Opinion(**o) for o in opinions],
            summary=analysis_result.summary or "",
            sentiment_breakdown=SentimentBreakdown(**sentiment_breakdown),
            market_potential=analysis_result.market_potential or "unknown",
            key_insights=[],  # Could be stored separately if needed
            recommendations=[]  # Could be stored separately if needed
        )
        
        return AnalysisResponse(
            session_id=analysis_id,
            product_idea=db_session.product_idea,
            analysis_results=analysis_results,
            metadata={
                "confidence_score": analysis_result.confidence_score,
                "created_at": analysis_result.created_at.isoformat()
            },
            status=db_session.status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
