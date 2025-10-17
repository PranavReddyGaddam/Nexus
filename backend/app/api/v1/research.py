"""Research session endpoints."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
from datetime import datetime

from app.schemas.research import (
    ResearchSessionCreate,
    ResearchSessionResponse,
    SessionStatus,
    FeedbackRoundRequest,
)
from app.schemas.feedback import FeedbackRoundResponse, FeedbackRound
from app.core.agents.agent_factory import get_agent_factory
from app.core.orchestration.feedback_loop import FeedbackLoopManager
from app.data.personas import get_all_personas, get_persona_by_id

router = APIRouter()

# In-memory storage (replace with database in production)
active_sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/sessions", response_model=ResearchSessionResponse)
async def create_research_session(session_request: ResearchSessionCreate):
    """Create a new research session."""
    session_id = str(uuid.uuid4())
    factory = get_agent_factory()
    
    # Select agents
    if session_request.auto_select_agents:
        all_personas = get_all_personas()
        selected_personas = factory.auto_select_agents(
            all_personas=all_personas,
            startup_idea=session_request.idea,
            max_agents=session_request.max_agents,
        )
    else:
        if not session_request.selected_agents:
            raise HTTPException(
                status_code=400,
                detail="Must provide selected_agents or set auto_select_agents=true"
            )
        selected_personas = [
            get_persona_by_id(agent_id)
            for agent_id in session_request.selected_agents
        ]
        selected_personas = [p for p in selected_personas if p is not None]
    
    if not selected_personas:
        raise HTTPException(
            status_code=400,
            detail="No valid agents could be selected"
        )
    
    # Create agents
    agents = factory.create_agents_from_personas(selected_personas)
    
    # Create feedback loop manager
    feedback_manager = FeedbackLoopManager(agents)
    feedback_manager.session_id = session_id
    
    # Store session
    active_sessions[session_id] = {
        "session_id": session_id,
        "idea": session_request.idea,
        "status": SessionStatus.CREATED,
        "selected_agents": [p.id for p in selected_personas],
        "current_round": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "feedback_manager": feedback_manager,
    }
    
    return ResearchSessionResponse(
        session_id=session_id,
        idea=session_request.idea,
        status=SessionStatus.CREATED,
        selected_agents=[p.id for p in selected_personas],
        current_round=0,
        created_at=active_sessions[session_id]["created_at"],
        updated_at=active_sessions[session_id]["updated_at"],
    )


@router.get("/sessions/{session_id}", response_model=ResearchSessionResponse)
async def get_research_session(session_id: str):
    """Get research session details."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    return ResearchSessionResponse(
        session_id=session["session_id"],
        idea=session["idea"],
        status=session["status"],
        selected_agents=session["selected_agents"],
        current_round=session["current_round"],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
    )


@router.post("/sessions/{session_id}/rounds", response_model=FeedbackRoundResponse)
async def start_feedback_round(
    session_id: str,
    round_request: FeedbackRoundRequest,
    background_tasks: BackgroundTasks,
):
    """Start a new feedback round for the session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    feedback_manager: FeedbackLoopManager = session["feedback_manager"]
    
    # Update session status
    session["status"] = SessionStatus.IN_PROGRESS
    session["updated_at"] = datetime.utcnow()
    
    # Execute feedback round
    try:
        feedback_round = await feedback_manager.execute_round(
            idea=session["idea"],
            user_input=round_request.user_message,
            mode="parallel",
        )
        
        session["current_round"] = feedback_round.round_number
        session["updated_at"] = datetime.utcnow()
        
        # Parse synthesis
        import json
        synthesis_data = json.loads(feedback_round.synthesis) if feedback_round.synthesis else None
        
        from app.schemas.feedback import FeedbackSynthesis
        synthesis = FeedbackSynthesis(**synthesis_data) if synthesis_data else None
        
        return FeedbackRoundResponse(
            round=feedback_round,
            synthesis=synthesis,
        )
        
    except Exception as e:
        session["status"] = SessionStatus.FAILED
        session["updated_at"] = datetime.utcnow()
        raise HTTPException(status_code=500, detail=f"Failed to execute round: {str(e)}")


@router.get("/sessions/{session_id}/rounds/{round_number}", response_model=FeedbackRound)
async def get_feedback_round(session_id: str, round_number: int):
    """Get a specific feedback round."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    feedback_manager: FeedbackLoopManager = session["feedback_manager"]
    
    if round_number < 1 or round_number > len(feedback_manager.rounds):
        raise HTTPException(status_code=404, detail="Round not found")
    
    return feedback_manager.rounds[round_number - 1]


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get a comprehensive summary of the research session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    feedback_manager: FeedbackLoopManager = session["feedback_manager"]
    
    return feedback_manager.get_session_summary()


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a research session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del active_sessions[session_id]
    
    return {"message": "Session deleted successfully"}

