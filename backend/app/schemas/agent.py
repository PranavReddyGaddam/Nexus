"""Agent-related schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    RESPONDING = "responding"
    COMPLETED = "completed"
    ERROR = "error"


class AgentSentiment(str, Enum):
    """Agent sentiment."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    CAUTIOUS = "cautious"
    NEGATIVE = "negative"


class AgentResponse(BaseModel):
    """Schema for an agent's response."""
    agent_id: str
    agent_name: str
    round_number: int
    sentiment: AgentSentiment
    summary: str = Field(..., description="Brief summary of feedback")
    detailed_feedback: str = Field(..., description="Detailed analysis")
    opportunities: List[str] = Field(..., description="Identified opportunities")
    concerns: List[str] = Field(..., description="Identified concerns")
    questions: List[str] = Field(default_factory=list, description="Questions for clarification")
    recommendations: List[str] = Field(..., description="Specific recommendations")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in assessment")
    responding_to: Optional[List[str]] = Field(
        None,
        description="Other agent IDs this response is addressing"
    )
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AgentMetadata(BaseModel):
    """Agent metadata."""
    agent_id: str
    persona_name: str
    title: str
    location: str
    industry: str
    expertise: List[str]
    experience: str
    total_sessions: int = 0
    average_response_time: float = 0.0


class AgentListResponse(BaseModel):
    """Response for listing agents."""
    agents: List[AgentMetadata]
    total: int


class StreamingChunk(BaseModel):
    """Schema for streaming response chunks."""
    agent_id: str
    chunk_type: str = Field(..., description="Type: 'text', 'summary', 'complete'")
    content: str
    metadata: Optional[Dict[str, Any]] = None

