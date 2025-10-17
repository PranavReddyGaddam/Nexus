"""
Voice Consultation Routes
Handles ElevenLabs voice consultation endpoints for persona-based conversations.
Uses Snowflake database for storage.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import json

from config.snowflake import get_snowflake_connection
from services.elevenlabs_service import ElevenLabsService

router = APIRouter()
elevenlabs_service = ElevenLabsService()

# Request/Response Models
class PersonaData(BaseModel):
    id: str
    name: str
    title: str
    location: str
    industry: str
    expertise: list[str]
    experience: str
    bio: str
    insights: Optional[list[str]] = None

class PreviousAnalysis(BaseModel):
    rating: Optional[float] = None
    sentiment: Optional[str] = None
    key_insight: Optional[str] = None

class StartConsultationRequest(BaseModel):
    persona: PersonaData
    startup_idea: Optional[str] = None
    session_id: Optional[int] = None
    previous_analysis: Optional[PreviousAnalysis] = None

class StartConsultationResponse(BaseModel):
    consultation_id: int
    agent_id: str
    persona_name: str
    message: str

class ConsultationDetailsResponse(BaseModel):
    consultation_id: int
    persona_name: str
    startup_idea: Optional[str]
    duration_seconds: Optional[float]
    transcript: Optional[str]
    status: str
    created_at: str
    ended_at: Optional[str]

@router.post("/voice/start-consultation", response_model=StartConsultationResponse)
async def start_voice_consultation(request: StartConsultationRequest):
    """
    Start a voice consultation with an expert persona.
    Creates or retrieves an ElevenLabs agent for the persona and returns connection details.
    """
    try:
        persona_dict = request.persona.dict()
        
        # Check if we already have an agent for this persona
        for conn in get_snowflake_connection():
            cursor = conn.cursor()
            try:
                # Check for existing agent
                cursor.execute(
                    "SELECT ID, AGENT_ID FROM ELEVENLABS_AGENTS WHERE PERSONA_ID = %(persona_id)s",
                    {'persona_id': request.persona.id}
                )
                existing_agent = cursor.fetchone()
                
                if existing_agent:
                    # Use existing agent
                    agent_table_id, agent_id = existing_agent
                    print(f"Using existing agent {agent_id} for persona {request.persona.id}")
                else:
                    # Create new agent
                    print(f"Creating new agent for persona {request.persona.id}")
                    
                    # Convert previous_analysis to dict if it exists
                    analysis_dict = None
                    if request.previous_analysis:
                        analysis_dict = {
                            'rating': request.previous_analysis.rating,
                            'sentiment': request.previous_analysis.sentiment,
                            'key_insight': request.previous_analysis.key_insight
                        }
                    
                    agent_data = await elevenlabs_service.create_agent_for_persona(
                        persona_dict,
                        request.startup_idea,
                        analysis_dict
                    )
                    
                    # Store agent in database
                    cursor.execute("""
                        INSERT INTO ELEVENLABS_AGENTS 
                        (PERSONA_ID, AGENT_ID, PERSONA_NAME, PERSONA_TITLE, 
                         PERSONA_LOCATION, PERSONA_INDUSTRY, SYSTEM_PROMPT)
                        VALUES (%(persona_id)s, %(agent_id)s, %(persona_name)s, %(persona_title)s, 
                                %(persona_location)s, %(persona_industry)s, %(system_prompt)s)
                    """, {
                        'persona_id': request.persona.id,
                        'agent_id': agent_data["agent_id"],
                        'persona_name': request.persona.name,
                        'persona_title': request.persona.title,
                        'persona_location': request.persona.location,
                        'persona_industry': request.persona.industry,
                        'system_prompt': agent_data["system_prompt"]
                    })
                    
                    # Get the newly created agent ID
                    cursor.execute(
                        "SELECT ID, AGENT_ID FROM ELEVENLABS_AGENTS WHERE PERSONA_ID = %(persona_id)s",
                        {'persona_id': request.persona.id}
                    )
                    result = cursor.fetchone()
                    agent_table_id, agent_id = result
                
                # Create consultation record and get the ID
                cursor.execute("""
                    INSERT INTO VOICE_CONSULTATIONS 
                    (SESSION_ID, AGENT_TABLE_ID, PERSONA_ID, STARTUP_IDEA, STATUS)
                    VALUES (%(session_id)s, %(agent_table_id)s, %(persona_id)s, %(startup_idea)s, %(status)s)
                """, {
                    'session_id': request.session_id,
                    'agent_table_id': agent_table_id,
                    'persona_id': request.persona.id,
                    'startup_idea': request.startup_idea,
                    'status': 'active'
                })
                
                # Get the last inserted consultation ID
                # In Snowflake, we query the table we just inserted into
                cursor.execute("""
                    SELECT ID FROM VOICE_CONSULTATIONS 
                    WHERE AGENT_TABLE_ID = %(agent_table_id)s 
                    AND PERSONA_ID = %(persona_id)s 
                    ORDER BY CREATED_AT DESC 
                    LIMIT 1
                """, {
                    'agent_table_id': agent_table_id,
                    'persona_id': request.persona.id
                })
                consultation_id = cursor.fetchone()[0]
                
                conn.commit()
                
                return StartConsultationResponse(
                    consultation_id=consultation_id,
                    agent_id=agent_id,
                    persona_name=request.persona.name,
                    message=f"Voice consultation with {request.persona.name} is ready!"
                )
            finally:
                cursor.close()
                
    except Exception as e:
        print(f"Error starting consultation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice/consultation/{consultation_id}", response_model=ConsultationDetailsResponse)
async def get_consultation_details(consultation_id: int):
    """
    Get details of a voice consultation including transcript if available
    """
    try:
        for conn in get_snowflake_connection():
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT 
                        vc.ID,
                        ea.PERSONA_NAME,
                        vc.STARTUP_IDEA,
                        vc.DURATION_SECONDS,
                        vc.TRANSCRIPT,
                        vc.STATUS,
                        vc.CREATED_AT,
                        vc.ENDED_AT
                    FROM VOICE_CONSULTATIONS vc
                    JOIN ELEVENLABS_AGENTS ea ON vc.AGENT_TABLE_ID = ea.ID
                    WHERE vc.ID = %(consultation_id)s
                """, {'consultation_id': consultation_id})
                
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(status_code=404, detail="Consultation not found")
                
                return ConsultationDetailsResponse(
                    consultation_id=result[0],
                    persona_name=result[1] or "Unknown",
                    startup_idea=result[2],
                    duration_seconds=result[3],
                    transcript=result[4],
                    status=result[5],
                    created_at=result[6].isoformat() if result[6] else "",
                    ended_at=result[7].isoformat() if result[7] else None
                )
            finally:
                cursor.close()
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching consultation details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/consultation/{consultation_id}/complete")
async def complete_consultation(
    consultation_id: int,
    conversation_id: Optional[str] = None
):
    """
    Mark a consultation as complete and optionally fetch transcript from ElevenLabs
    """
    try:
        transcript = None
        duration = None
        
        # If conversation_id provided, fetch transcript
        if conversation_id:
            try:
                conversation_details = await elevenlabs_service.get_conversation_details(conversation_id)
                
                # Extract transcript and convert to JSON string if it's a list
                if "transcript" in conversation_details:
                    transcript_data = conversation_details["transcript"]
                    # If it's a list, convert to JSON string
                    if isinstance(transcript_data, list):
                        transcript = json.dumps(transcript_data)
                    else:
                        transcript = str(transcript_data)
                
                # Calculate duration if available
                if "metadata" in conversation_details and "duration_seconds" in conversation_details["metadata"]:
                    duration = conversation_details["metadata"]["duration_seconds"]
                    
            except Exception as e:
                print(f"Error fetching conversation details: {e}")
        
        # Update consultation in database
        for conn in get_snowflake_connection():
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE VOICE_CONSULTATIONS
                    SET STATUS = %(status)s,
                        ENDED_AT = %(ended_at)s,
                        CONVERSATION_ID = %(conversation_id)s,
                        TRANSCRIPT = %(transcript)s,
                        DURATION_SECONDS = %(duration)s
                    WHERE ID = %(consultation_id)s
                """, {
                    'status': 'completed',
                    'ended_at': datetime.now(),
                    'conversation_id': conversation_id,
                    'transcript': transcript,
                    'duration': duration,
                    'consultation_id': consultation_id
                })
                
                conn.commit()
                
                return {
                    "status": "success",
                    "message": "Consultation marked as complete",
                    "consultation_id": consultation_id
                }
            finally:
                cursor.close()
        
    except Exception as e:
        print(f"Error completing consultation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice/consultations")
async def list_consultations(
    session_id: Optional[int] = None,
    persona_id: Optional[str] = None
):
    """
    List all voice consultations, optionally filtered by session or persona
    """
    try:
        for conn in get_snowflake_connection():
            cursor = conn.cursor()
            try:
                query = """
                    SELECT 
                        vc.ID,
                        ea.PERSONA_NAME,
                        vc.PERSONA_ID,
                        vc.STARTUP_IDEA,
                        vc.DURATION_SECONDS,
                        vc.STATUS,
                        vc.CREATED_AT,
                        CASE WHEN vc.TRANSCRIPT IS NOT NULL THEN TRUE ELSE FALSE END
                    FROM VOICE_CONSULTATIONS vc
                    JOIN ELEVENLABS_AGENTS ea ON vc.AGENT_TABLE_ID = ea.ID
                    WHERE 1=1
                """
                params: Dict[str, Any] = {}
                
                if session_id:
                    query += " AND vc.SESSION_ID = %(session_id)s"
                    params['session_id'] = session_id
                
                if persona_id:
                    query += " AND vc.PERSONA_ID = %(persona_id)s"
                    params['persona_id'] = persona_id
                
                query += " ORDER BY vc.CREATED_AT DESC"
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                consultations = []
                for row in results:
                    consultations.append({
                        "consultation_id": row[0],
                        "persona_name": row[1] or "Unknown",
                        "persona_id": row[2],
                        "startup_idea": row[3],
                        "duration_seconds": row[4],
                        "status": row[5],
                        "created_at": row[6].isoformat() if row[6] else "",
                        "has_transcript": row[7]
                    })
                
                return {
                    "consultations": consultations,
                    "total": len(consultations)
                }
            finally:
                cursor.close()
                
    except Exception as e:
        print(f"Error listing consultations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice/agents")
async def list_agents():
    """
    List all created ElevenLabs agents
    """
    try:
        for conn in get_snowflake_connection():
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT 
                        ID,
                        PERSONA_ID,
                        AGENT_ID,
                        PERSONA_NAME,
                        PERSONA_TITLE,
                        PERSONA_LOCATION,
                        PERSONA_INDUSTRY,
                        CREATED_AT
                    FROM ELEVENLABS_AGENTS
                    ORDER BY CREATED_AT DESC
                """)
                
                results = cursor.fetchall()
                
                agents = []
                for row in results:
                    agents.append({
                        "id": row[0],
                        "persona_id": row[1],
                        "agent_id": row[2],
                        "persona_name": row[3],
                        "persona_title": row[4],
                        "persona_location": row[5],
                        "persona_industry": row[6],
                        "created_at": row[7].isoformat() if row[7] else ""
                    })
                
                return {
                    "agents": agents,
                    "total": len(agents)
                }
            finally:
                cursor.close()
                
    except Exception as e:
        print(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
