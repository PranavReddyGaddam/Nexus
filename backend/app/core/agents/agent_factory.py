"""Factory for creating agent instances."""
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from app.core.agents.base_agent import BaseAgent
from app.core.llm.providers import LLMProvider, get_llm_provider
from app.schemas.persona import PersonaResponse


class AgentFactory:
    """Factory for creating and managing agent instances."""
    
    def __init__(self):
        """Initialize the agent factory."""
        self.llm_provider = get_llm_provider()
        self._agent_cache: Dict[str, BaseAgent] = {}
    
    def create_agent_from_persona(self, persona: PersonaResponse) -> BaseAgent:
        """
        Create an agent from a persona.
        
        Args:
            persona: Persona data
        
        Returns:
            BaseAgent instance
        """
        # Check cache first
        if persona.id in self._agent_cache:
            return self._agent_cache[persona.id]
        
        agent = BaseAgent(
            agent_id=persona.id,
            persona_name=persona.name,
            title=persona.title,
            location=persona.location,
            industry=persona.industry,
            expertise=persona.expertise,
            experience=persona.experience,
            bio=persona.bio,
            insights=persona.insights or [],
            llm_provider=self.llm_provider,
        )
        
        # Cache the agent
        self._agent_cache[persona.id] = agent
        
        return agent
    
    def create_agents_from_personas(
        self, 
        personas: List[PersonaResponse]
    ) -> List[BaseAgent]:
        """
        Create multiple agents from personas.
        
        Args:
            personas: List of persona data
        
        Returns:
            List of BaseAgent instances
        """
        return [self.create_agent_from_persona(p) for p in personas]
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get a cached agent by ID."""
        return self._agent_cache.get(agent_id)
    
    def clear_cache(self):
        """Clear the agent cache."""
        self._agent_cache.clear()
    
    @staticmethod
    def select_agents_by_criteria(
        all_personas: List[PersonaResponse],
        industry: Optional[str] = None,
        location: Optional[str] = None,
        expertise_areas: Optional[List[str]] = None,
        max_agents: int = 5,
    ) -> List[PersonaResponse]:
        """
        Select agents based on criteria.
        
        Args:
            all_personas: All available personas
            industry: Filter by industry
            location: Filter by location
            expertise_areas: Filter by expertise areas
            max_agents: Maximum number of agents to select
        
        Returns:
            List of selected personas
        """
        selected = all_personas.copy()
        
        # Apply filters
        if industry:
            selected = [
                p for p in selected 
                if industry.lower() in p.industry.lower()
            ]
        
        if location:
            selected = [
                p for p in selected 
                if location.lower() in p.location.lower()
            ]
        
        if expertise_areas:
            expertise_lower = [e.lower() for e in expertise_areas]
            selected = [
                p for p in selected
                if any(
                    any(exp_query in exp.lower() for exp_query in expertise_lower)
                    for exp in p.expertise
                )
            ]
        
        # Score and rank (simple scoring for now)
        scored_personas = []
        for persona in selected:
            score = 0
            
            # Industry match
            if industry and industry.lower() in persona.industry.lower():
                score += 3
            
            # Expertise match
            if expertise_areas:
                for exp in persona.expertise:
                    if any(e.lower() in exp.lower() for e in expertise_areas):
                        score += 2
            
            # Location diversity (prefer diverse locations)
            score += 1
            
            scored_personas.append((score, persona))
        
        # Sort by score and take top N
        scored_personas.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_personas[:max_agents]]
    
    @staticmethod
    def auto_select_agents(
        all_personas: List[PersonaResponse],
        startup_idea: Any,  # StartupIdea object
        max_agents: int = 5,
    ) -> List[PersonaResponse]:
        """
        Automatically select relevant agents based on startup idea.
        
        Args:
            all_personas: All available personas
            startup_idea: Startup idea to analyze
            max_agents: Maximum number of agents
        
        Returns:
            List of selected personas
        """
        # Extract key terms from the startup idea
        industry_terms = [startup_idea.industry]
        expertise_terms = []
        
        # Add technology stack as expertise terms
        if startup_idea.technology_stack:
            expertise_terms.extend(startup_idea.technology_stack)
        
        # Add business model terms
        if startup_idea.business_model:
            expertise_terms.append(startup_idea.business_model)
        
        # Use criteria-based selection
        return AgentFactory.select_agents_by_criteria(
            all_personas=all_personas,
            industry=startup_idea.industry,
            expertise_areas=expertise_terms if expertise_terms else None,
            max_agents=max_agents,
        )


# Global factory instance
_factory_instance: Optional[AgentFactory] = None


def get_agent_factory() -> AgentFactory:
    """Get the global agent factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AgentFactory()
    return _factory_instance

