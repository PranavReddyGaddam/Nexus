"""Feedback round schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.agent import AgentResponse, AgentSentiment


class FeedbackRoundStatus(str, Enum):
    """Feedback round status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class FeedbackRound(BaseModel):
    """Feedback round details."""
    round_id: str
    session_id: str
    round_number: int
    status: FeedbackRoundStatus
    user_input: Optional[str] = None
    agent_responses: List[AgentResponse]
    synthesis: Optional[str] = None
    consensus_points: List[str] = Field(default_factory=list)
    divergent_points: List[Dict[str, Any]] = Field(default_factory=list)
    overall_sentiment: AgentSentiment
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FeedbackSynthesis(BaseModel):
    """Synthesized feedback from multiple agents."""
    round_number: int
    total_agents: int
    consensus_insights: List[str] = Field(..., description="Points where agents agree")
    divergent_opinions: List[Dict[str, str]] = Field(
        ...,
        description="Points where agents disagree"
    )
    top_opportunities: List[str] = Field(..., description="Top opportunities identified")
    top_concerns: List[str] = Field(..., description="Top concerns identified")
    priority_questions: List[str] = Field(..., description="Most important questions")
    next_steps_suggested: List[str] = Field(..., description="Suggested next steps")
    overall_sentiment: AgentSentiment
    confidence_level: str = Field(..., description="Overall confidence level")


class FeedbackRoundResponse(BaseModel):
    """Response after completing a feedback round."""
    round: FeedbackRound
    synthesis: FeedbackSynthesis


from enum import Enum

