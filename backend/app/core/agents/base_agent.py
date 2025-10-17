"""Base agent class for expert personas."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from app.schemas.agent import AgentResponse, AgentSentiment
from app.schemas.research import StartupIdea
from app.core.llm.providers import LLMProvider


class BaseAgent(ABC):
    """Base class for all expert agents."""
    
    def __init__(
        self,
        agent_id: str,
        persona_name: str,
        title: str,
        location: str,
        industry: str,
        expertise: List[str],
        experience: str,
        bio: str,
        insights: List[str],
        llm_provider: LLMProvider,
    ):
        """Initialize the agent."""
        self.agent_id = agent_id
        self.persona_name = persona_name
        self.title = title
        self.location = location
        self.industry = industry
        self.expertise = expertise
        self.experience = experience
        self.bio = bio
        self.insights = insights
        self.llm_provider = llm_provider
        
        # Context management
        self.conversation_history: List[Dict[str, Any]] = []
        self.previous_responses: List[str] = []
    
    def get_system_prompt(self) -> str:
        """Generate the system prompt for this agent."""
        return f"""You are {self.persona_name}, {self.title} based in {self.location}.

Your Background:
{self.bio}

Your Expertise:
{', '.join(self.expertise)}

Experience: {self.experience} in {self.industry}

Your Key Insights:
{chr(10).join(f'- {insight}' for insight in self.insights)}

Role: You are evaluating a startup idea as part of a multi-expert panel. Provide honest, 
professional feedback based on your expertise and experience. Be specific, actionable, and 
consider both opportunities and risks. Your perspective represents the {self.industry} 
sector from a {self.location} market viewpoint.

Communication Style: Professional yet conversational. Use specific examples when possible.
Be constructive in criticism and highlight both strengths and areas for improvement."""
    
    def get_analysis_prompt(
        self,
        idea: StartupIdea,
        round_number: int,
        user_context: Optional[str] = None,
        other_agent_responses: Optional[List[AgentResponse]] = None,
    ) -> str:
        """Generate the prompt for analyzing the startup idea."""
        
        prompt = f"""## Startup Idea Analysis Request - Round {round_number}

**Idea Title:** {idea.title}

**Description:**
{idea.description}

**Target Market:** {idea.target_market}
**Industry:** {idea.industry}
**Business Model:** {idea.business_model or 'Not specified'}
**Stage:** {idea.stage}
"""
        
        if idea.technology_stack:
            prompt += f"\n**Technology Stack:** {', '.join(idea.technology_stack)}\n"
        
        if idea.additional_context:
            prompt += f"\n**Additional Context:**\n{idea.additional_context}\n"
        
        if user_context:
            prompt += f"\n**User's Additional Input:**\n{user_context}\n"
        
        if other_agent_responses and len(other_agent_responses) > 0:
            prompt += "\n\n## Other Expert Opinions:\n"
            for response in other_agent_responses:
                prompt += f"\n**{response.agent_name}** ({response.sentiment}):\n"
                prompt += f"{response.summary}\n"
        
        prompt += f"""

Please provide your analysis in the following structured format:

1. **Summary** (2-3 sentences): Your overall assessment of this idea

2. **Opportunities** (3-5 points): Specific opportunities you see based on your expertise

3. **Concerns** (3-5 points): Specific concerns or challenges you identify

4. **Questions** (2-4 questions): Important questions that need to be answered

5. **Recommendations** (3-5 points): Specific, actionable recommendations

6. **Sentiment**: One of: very_positive, positive, neutral, cautious, negative

7. **Confidence Score** (0.0-1.0): How confident are you in your assessment

Remember to:
- Draw on your specific expertise in {', '.join(self.expertise[:3])}
- Consider the {self.location} market perspective
- Reference relevant trends or examples from your experience
- Be specific and actionable in your feedback
"""
        
        if round_number > 1:
            prompt += "\n- Build upon or respond to insights from other experts if relevant"
        
        return prompt
    
    async def analyze(
        self,
        idea: StartupIdea,
        round_number: int = 1,
        user_context: Optional[str] = None,
        other_agent_responses: Optional[List[AgentResponse]] = None,
        stream: bool = False,
    ) -> AgentResponse:
        """
        Analyze the startup idea and generate feedback.
        
        Args:
            idea: The startup idea to analyze
            round_number: Current feedback round number
            user_context: Additional context from the user
            other_agent_responses: Responses from other agents to consider
            stream: Whether to stream the response
        
        Returns:
            AgentResponse with structured feedback
        """
        system_prompt = self.get_system_prompt()
        analysis_prompt = self.get_analysis_prompt(
            idea, round_number, user_context, other_agent_responses
        )
        
        # Call LLM
        response_text = await self.llm_provider.generate(
            system_prompt=system_prompt,
            user_prompt=analysis_prompt,
            temperature=0.7,
            max_tokens=2000,
        )
        
        # Parse the response
        parsed_response = self._parse_response(response_text)
        
        # Create AgentResponse object
        agent_response = AgentResponse(
            agent_id=self.agent_id,
            agent_name=self.persona_name,
            round_number=round_number,
            sentiment=parsed_response.get("sentiment", AgentSentiment.NEUTRAL),
            summary=parsed_response.get("summary", ""),
            detailed_feedback=response_text,
            opportunities=parsed_response.get("opportunities", []),
            concerns=parsed_response.get("concerns", []),
            questions=parsed_response.get("questions", []),
            recommendations=parsed_response.get("recommendations", []),
            confidence_score=parsed_response.get("confidence_score", 0.7),
            responding_to=self._identify_responding_to(other_agent_responses),
            timestamp=datetime.utcnow(),
        )
        
        # Update conversation history
        self.conversation_history.append({
            "round": round_number,
            "idea": idea.model_dump(),
            "response": agent_response.model_dump(),
        })
        
        return agent_response
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM response into structured components."""
        parsed = {
            "summary": "",
            "opportunities": [],
            "concerns": [],
            "questions": [],
            "recommendations": [],
            "sentiment": AgentSentiment.NEUTRAL,
            "confidence_score": 0.7,
        }
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Detect sections
            if '**Summary**' in line or 'Summary:' in line:
                current_section = 'summary'
                continue
            elif '**Opportunities**' in line or 'Opportunities:' in line:
                current_section = 'opportunities'
                continue
            elif '**Concerns**' in line or 'Concerns:' in line:
                current_section = 'concerns'
                continue
            elif '**Questions**' in line or 'Questions:' in line:
                current_section = 'questions'
                continue
            elif '**Recommendations**' in line or 'Recommendations:' in line:
                current_section = 'recommendations'
                continue
            elif '**Sentiment**' in line or 'Sentiment:' in line:
                current_section = 'sentiment'
                # Try to extract sentiment from the line
                sentiment_str = line.lower()
                if 'very_positive' in sentiment_str or 'very positive' in sentiment_str:
                    parsed['sentiment'] = AgentSentiment.VERY_POSITIVE
                elif 'positive' in sentiment_str:
                    parsed['sentiment'] = AgentSentiment.POSITIVE
                elif 'cautious' in sentiment_str:
                    parsed['sentiment'] = AgentSentiment.CAUTIOUS
                elif 'negative' in sentiment_str:
                    parsed['sentiment'] = AgentSentiment.NEGATIVE
                continue
            elif '**Confidence Score**' in line or 'Confidence:' in line:
                current_section = 'confidence'
                # Try to extract confidence score
                try:
                    import re
                    score_match = re.search(r'([0-9]*\.?[0-9]+)', line)
                    if score_match:
                        score = float(score_match.group(1))
                        parsed['confidence_score'] = min(max(score, 0.0), 1.0)
                except:
                    pass
                continue
            
            # Add content to appropriate section
            if current_section == 'summary' and line:
                parsed['summary'] += line + ' '
            elif current_section in ['opportunities', 'concerns', 'questions', 'recommendations']:
                if line and (line.startswith('-') or line.startswith('•') or 
                           line[0].isdigit() or line.startswith('*')):
                    # Remove list markers
                    cleaned = line.lstrip('-•*0123456789. ')
                    if cleaned:
                        parsed[current_section].append(cleaned)
        
        # Clean up summary
        parsed['summary'] = parsed['summary'].strip()
        
        return parsed
    
    def _identify_responding_to(
        self, 
        other_responses: Optional[List[AgentResponse]]
    ) -> Optional[List[str]]:
        """Identify which other agents this response is addressing."""
        if not other_responses:
            return None
        
        # Simple heuristic: we're responding to all other agents in the round
        return [r.agent_id for r in other_responses]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "agent_id": self.agent_id,
            "persona_name": self.persona_name,
            "title": self.title,
            "location": self.location,
            "industry": self.industry,
            "expertise": self.expertise,
            "experience": self.experience,
        }

