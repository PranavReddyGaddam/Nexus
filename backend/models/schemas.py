from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Input schemas
class AnalysisRequest(BaseModel):
    product_idea: str

class SessionCreate(BaseModel):
    product_idea: str

# Output schemas
class Persona(BaseModel):
    id: int
    name: str
    age: int
    location: str
    occupation: str
    description: str

class Opinion(BaseModel):
    id: int
    persona_id: int
    content: str
    sentiment: str  # positive, negative, neutral

class SentimentBreakdown(BaseModel):
    positive: int
    negative: int
    neutral: int
    total: int

class AnalysisResults(BaseModel):
    personas: List[Persona]
    opinions: List[Opinion]
    summary: str
    sentiment_breakdown: SentimentBreakdown
    market_potential: str
    key_insights: List[str]
    recommendations: List[str]

class AnalysisResponse(BaseModel):
    session_id: int
    product_idea: str
    analysis_results: Optional[AnalysisResults] = None
    metadata: Dict[str, Any]
    status: str

class SessionResponse(BaseModel):
    id: int
    product_idea: str
    status: str
    created_at: datetime
    updated_at: datetime

class WebSocketMessage(BaseModel):
    type: str  # status_update, results, error
    session_id: int
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# --------------------------
# New MVP OpenAI ranking API
# --------------------------

class IdeaAnalyzeRequest(BaseModel):
    idea: str
    max_personas: int = 5

class PersonaCard(BaseModel):
    id: str
    name: str
    title: str
    location: str
    industry: str
    expertise: list[str]
    experience: str

class PersonaEvaluation(BaseModel):
    persona: PersonaCard
    relevanceScore: float
    rating: int
    sentiment: str
    keyInsight: str
    reason: str

class IdeaAnalyzeSummary(BaseModel):
    averageRating: float
    overallSentiment: str
    topConcerns: list[str]
    topOpportunities: list[str]

class IdeaAnalyzeResponse(BaseModel):
    enhancedIdea: str
    results: list[PersonaEvaluation]
    summary: IdeaAnalyzeSummary
