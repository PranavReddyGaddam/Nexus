"""Persona management endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.persona import PersonaResponse, PersonaListResponse
from app.data.personas import get_all_personas, get_persona_by_id

router = APIRouter()


@router.get("/", response_model=PersonaListResponse)
async def list_personas():
    """List all available personas."""
    personas = get_all_personas()
    return PersonaListResponse(
        personas=personas,
        total=len(personas),
    )


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(persona_id: str):
    """Get a specific persona by ID."""
    persona = get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.get("/location/{location_name}", response_model=List[PersonaResponse])
async def get_personas_by_location(location_name: str):
    """Get personas for a specific location."""
    from app.data.personas import get_personas_by_location
    personas = get_personas_by_location(location_name)
    if not personas:
        raise HTTPException(
            status_code=404,
            detail=f"No personas found for location: {location_name}"
        )
    return personas

