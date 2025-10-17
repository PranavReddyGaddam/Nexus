"""Idea analysis endpoint using LLM to select and rate personas."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.core.llm.providers import get_llm_provider
from app.data.personas import get_all_personas, get_persona_by_id

router = APIRouter()


class PersonaInfo(BaseModel):
    """Minimal persona info for LLM analysis."""
    id: str
    name: str
    industry: str
    expertise: List[str]
    location: str


class IdeaAnalysisRequest(BaseModel):
    """Request to analyze a startup idea."""
    idea: str = Field(..., min_length=10, description="The startup idea to analyze")
    max_agents: int = Field(default=5, ge=1, le=10, description="Maximum number of agents to consult")
    available_personas: List[PersonaInfo] = Field(
        default_factory=list,
        description="Available personas (optional, will use all if not provided)"
    )


class PersonaRatingResponse(BaseModel):
    """Response with persona rating."""
    persona_id: str
    rating: float = Field(..., ge=0, le=10, description="Rating from 0-10")
    sentiment: str = Field(..., description="positive, neutral, or cautious")
    key_insight: str = Field(..., description="Key insight about the idea")
    relevance_score: float = Field(..., ge=0, le=1, description="How relevant this expert is")
    reasoning: str = Field(..., description="Why this expert was selected")


class IdeaAnalysisResponse(BaseModel):
    """Complete analysis response."""
    results: List[PersonaRatingResponse]
    summary: Dict[str, Any]


async def select_and_rate_personas_with_llm(
    idea: str,
    available_personas: List[PersonaInfo],
    max_agents: int
) -> List[PersonaRatingResponse]:
    """
    Use LLM to intelligently select personas and rate the idea.
    
    This is the core AI logic that:
    1. Analyzes the startup idea
    2. Selects the most relevant expert personas
    3. Provides ratings and insights from each expert's perspective
    """
    llm = get_llm_provider()
    
    # Create a prompt for the LLM to select relevant personas
    personas_description = "\n".join([
        f"{i+1}. {p.name} (ID: {p.id})\n"
        f"   Industry: {p.industry}\n"
        f"   Expertise: {', '.join(p.expertise)}\n"
        f"   Location: {p.location}"
        for i, p in enumerate(available_personas)
    ])
    
    system_prompt = """You are an expert business analyst who helps evaluate startup ideas by selecting the most relevant industry experts and simulating their feedback.

Your task:
1. Analyze the startup idea
2. Select the most relevant experts from the list (maximum specified by user)
3. For each expert, provide:
   - A rating (0-10) of how promising they think this idea is
   - Their sentiment (positive/neutral/cautious)
   - A key insight from their perspective
   - Why they are relevant to this idea

Be realistic and critical. Consider market fit, competition, execution challenges, and opportunities."""

    user_prompt = f"""Startup Idea: "{idea}"

Available Experts:
{personas_description}

Please select up to {max_agents} most relevant experts and provide their analysis.

Respond in JSON format:
{{
  "selected_experts": [
    {{
      "persona_id": "expert_id",
      "relevance_score": 0.95,
      "reasoning": "Why this expert is relevant",
      "rating": 7.5,
      "sentiment": "positive|neutral|cautious",
      "key_insight": "Their main insight about the idea"
    }}
  ]
}}"""

    # Call the LLM
    response_text = await llm.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
        max_tokens=2000,
    )
    
    # Parse the JSON response
    import json
    try:
        # Try to extract JSON from the response
        # LLMs sometimes wrap JSON in markdown code blocks
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()
        
        parsed = json.loads(json_str)
        selected = parsed.get("selected_experts", [])
        
        # Convert to PersonaRatingResponse
        results = []
        for expert in selected[:max_agents]:
            results.append(PersonaRatingResponse(
                persona_id=expert["persona_id"],
                rating=float(expert["rating"]),
                sentiment=expert["sentiment"],
                key_insight=expert["key_insight"],
                relevance_score=float(expert.get("relevance_score", 0.8)),
                reasoning=expert.get("reasoning", "Expert in relevant field"),
            ))
        
        return results
        
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM response: {str(e)}"
        )


@router.post("/analyze-idea", response_model=IdeaAnalysisResponse)
async def analyze_startup_idea(request: IdeaAnalysisRequest):
    """
    Analyze a startup idea using AI-powered expert personas.
    
    This endpoint:
    1. Takes a startup idea description
    2. Uses LLM to select the most relevant expert personas
    3. Simulates each expert's analysis and rating
    4. Returns structured feedback with ratings and insights
    """
    # Get all personas if not provided
    if not request.available_personas:
        all_personas = get_all_personas()
        available_personas = [
            PersonaInfo(
                id=p.id,
                name=p.name,
                industry=p.industry,
                expertise=p.expertise,
                location=p.location,
            )
            for p in all_personas
        ]
    else:
        available_personas = request.available_personas
    
    # Use LLM to select and rate personas
    results = await select_and_rate_personas_with_llm(
        idea=request.idea,
        available_personas=available_personas,
        max_agents=request.max_agents,
    )
    
    # Calculate summary statistics
    if results:
        avg_rating = sum(r.rating for r in results) / len(results)
        positive_count = sum(1 for r in results if r.sentiment == "positive")
        
        overall_sentiment = (
            "positive" if positive_count / len(results) >= 0.6
            else "neutral" if positive_count / len(results) >= 0.3
            else "cautious"
        )
    else:
        avg_rating = 0.0
        overall_sentiment = "neutral"
    
    summary = {
        "average_rating": round(avg_rating, 1),
        "overall_sentiment": overall_sentiment,
        "total_experts": len(results),
        "top_concerns": [
            r.key_insight for r in results if r.rating < 7
        ][:3],
        "top_opportunities": [
            r.key_insight for r in results if r.rating >= 8
        ][:3],
    }
    
    return IdeaAnalysisResponse(
        results=results,
        summary=summary,
    )

