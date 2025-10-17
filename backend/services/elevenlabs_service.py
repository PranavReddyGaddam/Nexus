"""
ElevenLabs Service for managing conversational AI agents.
Handles agent creation, configuration, and conversation management.
"""
import httpx
import json
from typing import Dict, Any, Optional
from config.settings import settings

class ElevenLabsService:
    """Service to manage ElevenLabs AI agents for persona-based voice consultations"""
    
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _create_system_prompt(
        self, 
        persona: Dict[str, Any], 
        startup_context: Optional[str] = None,
        previous_analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a detailed system prompt for the agent based on persona information
        """
        prompt = f"""You are {persona['name']}, a {persona['title']} based in {persona['location']}.

BACKGROUND:
{persona['bio']}

EXPERTISE:
You specialize in: {', '.join(persona['expertise'])}

YOUR ROLE:
You are conducting a voice consultation to provide expert feedback and insights on startup ideas and business strategies. Draw upon your {persona['experience']} of experience in {persona['industry']}.

KEY INSIGHTS YOU'VE OBSERVED:
"""
        
        # Add persona insights if available
        if 'insights' in persona and persona['insights']:
            for insight in persona['insights']:
                prompt += f"- {insight}\n"
        
        # Add startup context if provided
        if startup_context:
            prompt += f"\n\nCONTEXT FOR THIS CONSULTATION:\nThe entrepreneur is working on: {startup_context}\n"
        
        # Add previous analysis if provided
        if previous_analysis:
            prompt += f"\n\nYOUR PREVIOUS ANALYSIS:\n"
            prompt += f"You already provided initial feedback on this idea:\n"
            if previous_analysis.get('rating'):
                prompt += f"- Rating: {previous_analysis['rating']}/10\n"
            if previous_analysis.get('sentiment'):
                prompt += f"- Sentiment: {previous_analysis['sentiment']}\n"
            if previous_analysis.get('key_insight'):
                prompt += f"- Key Insight: {previous_analysis['key_insight']}\n"
            prompt += "\nIMPORTANT: Build upon this initial analysis in your conversation. Reference your previous feedback naturally and dive deeper into the points you raised. The entrepreneur has already seen your written analysis and wants to discuss it further.\n"
        
        prompt += """
CONVERSATION STYLE:
- Be conversational and approachable, like speaking with a knowledgeable friend
- Ask clarifying questions to better understand their business
- Provide specific, actionable feedback based on your expertise
- Share relevant examples from your experience
- Be honest about potential challenges while remaining encouraging
- Keep responses concise (2-3 sentences typically) to maintain natural conversation flow

Remember: You're having a real-time voice conversation. Be natural, authentic, and speak as yourself."""
        
        return prompt
    
    async def create_agent_for_persona(
        self,
        persona: Dict[str, Any],
        startup_idea: Optional[str] = None,
        previous_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an ElevenLabs conversational AI agent for a specific persona
        """
        system_prompt = self._create_system_prompt(persona, startup_idea, previous_analysis)
        
        # Select an appropriate voice (you can customize this based on persona characteristics)
        voice_id = self._select_voice_for_persona(persona)
        
        # Correct API structure according to ElevenLabs schema
        # Create contextual first message
        if previous_analysis and previous_analysis.get('key_insight'):
            first_message = f"Hello! I'm {persona['name']}. I've reviewed your startup idea and provided some initial feedback. I gave it a {previous_analysis.get('rating', 'N/A')}/10. I'm here to dive deeper into my thoughts and answer any questions you have about my analysis. What would you like to discuss first?"
        else:
            first_message = f"Hello! I'm {persona['name']}, {persona['title']}. I'm excited to hear about your startup idea and provide some insights from my experience in {persona['industry']}. What would you like to discuss?"
        
        agent_config = {
            "conversation_config": {
                "agent": {
                    "first_message": first_message,
                    "language": "en",
                    "prompt": {
                        "prompt": system_prompt,
                        "llm": "gpt-4o",
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                },
                "tts": {
                    "voice_id": voice_id,
                    "model_id": "eleven_turbo_v2"
                }
            },
            "name": f"{persona['name']} - Consultant"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/convai/agents/create",
                    headers=self.headers,
                    json=agent_config
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "agent_id": result["agent_id"],
                    "persona_id": persona["id"],
                    "persona_name": persona["name"],
                    "system_prompt": system_prompt
                }
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
                print(f"ElevenLabs API Error Response: {json.dumps(error_detail, indent=2)}")
            except:
                error_detail = e.response.text
                print(f"ElevenLabs API Error Text: {error_detail}")
            print(f"Error creating ElevenLabs agent: {e}")
            print(f"Request payload: {json.dumps(agent_config, indent=2)}")
            raise Exception(f"Failed to create agent: {str(e)} - {error_detail}")
        except httpx.HTTPError as e:
            print(f"Error creating ElevenLabs agent: {e}")
            raise Exception(f"Failed to create agent: {str(e)}")
    
    def _select_voice_for_persona(self, persona: Dict[str, Any]) -> str:
        """
        Select an appropriate voice ID based on persona characteristics
        You can expand this logic to match voices to persona demographics
        """
        # Default voices - you can customize this mapping
        # ElevenLabs has many voices available in their library
        default_voices = {
            "male": "21m00Tcm4TlvDq8ikWAM",  # Example male voice
            "female": "EXAVITQu4vr4xnSDxMaL",  # Example female voice
        }
        
        # Simple gender detection from name (can be improved)
        # For now, using a default professional voice
        return "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional female voice
    
    async def get_agent_link(self, agent_id: str) -> Dict[str, str]:
        """
        Get the agent link (for public agents, this is just the agent ID)
        """
        return {
            "agent_id": agent_id,
            "agent_url": f"https://elevenlabs.io/app/conversational-ai/{agent_id}"
        }
    
    async def get_conversation_details(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve details and transcript of a completed conversation
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/convai/conversations/{conversation_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching conversation details: {e}")
            raise Exception(f"Failed to fetch conversation: {str(e)}")
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent when no longer needed
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/convai/agents/{agent_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            print(f"Error deleting agent: {e}")
            return False

