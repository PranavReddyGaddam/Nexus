"""Research session schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Research session status."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class StartupIdea(BaseModel):
    """Startup idea details."""
    title: str = Field(..., description="Startup idea title", min_length=5, max_length=200)
    description: str = Field(..., description="Detailed description", min_length=20)
    target_market: str = Field(..., description="Target market/geography")
    industry: str = Field(..., description="Industry vertical")
    business_model: Optional[str] = Field(None, description="Business model")
    technology_stack: Optional[List[str]] = Field(None, description="Key technologies")
    stage: Optional[str] = Field(default="ideation", description="Current stage")
    additional_context: Optional[Dict[str, Any]] = None


class ResearchSessionCreate(BaseModel):
    """Schema for creating a research session."""
    idea: StartupIdea
    selected_agents: Optional[List[str]] = Field(
        None, 
        description="Specific agent IDs to use, if not provided will auto-select"
    )
    auto_select_agents: bool = Field(
        default=True,
        description="Automatically select relevant agents"
    )
    max_agents: int = Field(default=5, ge=1, le=10)


class ResearchSessionResponse(BaseModel):
    """Schema for research session response."""
    session_id: str
    idea: StartupIdea
    status: SessionStatus
    selected_agents: List[str]
    current_round: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackRoundRequest(BaseModel):
    """Request to start a new feedback round."""
    user_message: Optional[str] = Field(
        None,
        description="User's refinement or additional context"
    )
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Specific areas to focus on in this round"
    )


class MarketOpportunity(BaseModel):
    """Market opportunity assessment."""
    score: float = Field(..., ge=0, le=10, description="Opportunity score (0-10)")
    size_estimate: str = Field(..., description="Market size estimate")
    growth_potential: str = Field(..., description="Growth potential")
    key_factors: List[str] = Field(..., description="Key success factors")


class RiskAssessment(BaseModel):
    """Risk assessment."""
    risk_level: str = Field(..., description="Overall risk level")
    key_risks: List[str] = Field(..., description="Identified risks")
    mitigation_strategies: List[str] = Field(..., description="Risk mitigation strategies")


class CompetitiveLandscape(BaseModel):
    """Competitive landscape analysis."""
    competition_level: str = Field(..., description="Competition intensity")
    key_competitors: List[str] = Field(default_factory=list)
    differentiation_opportunities: List[str] = Field(..., description="Ways to differentiate")


class SessionSummary(BaseModel):
    """Summary of a research session."""
    session_id: str
    idea_title: str
    total_rounds: int
    agent_count: int
    market_opportunity: MarketOpportunity
    risk_assessment: RiskAssessment
    competitive_landscape: CompetitiveLandscape
    consensus_insights: List[str]
    divergent_opinions: List[Dict[str, str]]
    recommendations: List[str]
    overall_sentiment: str
    next_steps: List[str]

