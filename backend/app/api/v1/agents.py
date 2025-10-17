"""Agent management endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.agent import AgentMetadata, AgentListResponse
from app.schemas.persona import AgentSelectionCriteria, PersonaResponse
from app.core.agents.agent_factory import get_agent_factory
from app.data.personas import get_all_personas

router = APIRouter()


@router.get("/", response_model=AgentListResponse)
async def list_agents():
    """List all available agents."""
    personas = get_all_personas()
    
    agent_metadata = [
        AgentMetadata(
            agent_id=p.id,
            persona_name=p.name,
            title=p.title,
            location=p.location,
            industry=p.industry,
            expertise=p.expertise,
            experience=p.experience,
            total_sessions=0,  # Would come from database
            average_response_time=0.0,  # Would come from database
        )
        for p in personas
    ]
    
    return AgentListResponse(
        agents=agent_metadata,
        total=len(agent_metadata),
    )


@router.get("/{agent_id}", response_model=AgentMetadata)
async def get_agent(agent_id: str):
    """Get specific agent metadata."""
    from app.data.personas import get_persona_by_id
    
    persona = get_persona_by_id(agent_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentMetadata(
        agent_id=persona.id,
        persona_name=persona.name,
        title=persona.title,
        location=persona.location,
        industry=persona.industry,
        expertise=persona.expertise,
        experience=persona.experience,
        total_sessions=0,
        average_response_time=0.0,
    )


@router.post("/select", response_model=List[PersonaResponse])
async def select_agents(criteria: AgentSelectionCriteria):
    """Select agents based on criteria."""
    factory = get_agent_factory()
    all_personas = get_all_personas()
    
    selected = factory.select_agents_by_criteria(
        all_personas=all_personas,
        industry=criteria.industry,
        location=criteria.location,
        expertise_areas=criteria.expertise_areas,
        max_agents=criteria.max_agents,
    )
    
    if not selected:
        raise HTTPException(
            status_code=404,
            detail="No agents match the specified criteria"
        )
    
    return selected

