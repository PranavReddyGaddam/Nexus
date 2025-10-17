"""Persona schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PersonaBase(BaseModel):
    """Base persona schema."""
    name: str = Field(..., description="Full name of the persona")
    title: str = Field(..., description="Professional title")
    location: str = Field(..., description="Primary location")
    industry: str = Field(..., description="Primary industry")
    expertise: List[str] = Field(..., description="Areas of expertise")
    experience: str = Field(..., description="Years of experience")
    bio: str = Field(..., description="Professional biography")


class PersonaCreate(PersonaBase):
    """Schema for creating a persona."""
    insights: Optional[List[str]] = Field(default=None, description="Key insights")


class PersonaResponse(PersonaBase):
    """Schema for persona response."""
    id: str
    insights: List[str] = Field(default_factory=list)
    created_at: datetime
    
    class Config:
        from_attributes = True


class PersonaListResponse(BaseModel):
    """Schema for listing personas."""
    personas: List[PersonaResponse]
    total: int


class AgentSelectionCriteria(BaseModel):
    """Criteria for selecting agents."""
    industry: Optional[str] = None
    location: Optional[str] = None
    expertise_areas: Optional[List[str]] = None
    min_experience_years: Optional[int] = None
    max_agents: int = Field(default=5, ge=1, le=10)

