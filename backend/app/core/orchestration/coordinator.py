"""Multi-agent coordinator for parallel execution."""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.agents.base_agent import BaseAgent
from app.schemas.research import StartupIdea
from app.schemas.agent import AgentResponse
from app.config import settings


class MultiAgentCoordinator:
    """Coordinates multiple agents working in parallel."""
    
    def __init__(self, agents: List[BaseAgent]):
        """
        Initialize the coordinator.
        
        Args:
            agents: List of agents to coordinate
        """
        self.agents = agents
        self.timeout = settings.default_agent_timeout
    
    async def run_parallel_analysis(
        self,
        idea: StartupIdea,
        round_number: int = 1,
        user_context: Optional[str] = None,
        previous_responses: Optional[List[AgentResponse]] = None,
    ) -> List[AgentResponse]:
        """
        Run analysis with all agents in parallel.
        
        Args:
            idea: Startup idea to analyze
            round_number: Current feedback round
            user_context: Additional user context
            previous_responses: Responses from previous rounds
        
        Returns:
            List of agent responses
        """
        # Create tasks for all agents
        tasks = []
        for agent in self.agents:
            task = asyncio.create_task(
                self._run_agent_with_timeout(
                    agent=agent,
                    idea=idea,
                    round_number=round_number,
                    user_context=user_context,
                    other_responses=previous_responses,
                )
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors and return successful responses
        successful_responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Agent {self.agents[i].persona_name} failed: {str(result)}")
            elif result is not None:
                successful_responses.append(result)
        
        return successful_responses
    
    async def _run_agent_with_timeout(
        self,
        agent: BaseAgent,
        idea: StartupIdea,
        round_number: int,
        user_context: Optional[str],
        other_responses: Optional[List[AgentResponse]],
    ) -> Optional[AgentResponse]:
        """Run a single agent with timeout."""
        try:
            response = await asyncio.wait_for(
                agent.analyze(
                    idea=idea,
                    round_number=round_number,
                    user_context=user_context,
                    other_agent_responses=other_responses,
                ),
                timeout=self.timeout,
            )
            return response
        except asyncio.TimeoutError:
            print(f"Agent {agent.persona_name} timed out after {self.timeout}s")
            return None
        except Exception as e:
            print(f"Agent {agent.persona_name} error: {str(e)}")
            return None
    
    async def run_sequential_dialogue(
        self,
        idea: StartupIdea,
        round_number: int,
        user_context: Optional[str] = None,
    ) -> List[AgentResponse]:
        """
        Run agents sequentially so they can build on each other's responses.
        
        Args:
            idea: Startup idea to analyze
            round_number: Current feedback round
            user_context: Additional user context
        
        Returns:
            List of agent responses
        """
        responses: List[AgentResponse] = []
        
        for agent in self.agents:
            try:
                # Each agent sees all previous responses in this round
                response = await asyncio.wait_for(
                    agent.analyze(
                        idea=idea,
                        round_number=round_number,
                        user_context=user_context,
                        other_agent_responses=responses if responses else None,
                    ),
                    timeout=self.timeout,
                )
                responses.append(response)
            except asyncio.TimeoutError:
                print(f"Agent {agent.persona_name} timed out")
            except Exception as e:
                print(f"Agent {agent.persona_name} error: {str(e)}")
        
        return responses
    
    def get_agent_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all agents."""
        return [agent.get_metadata() for agent in self.agents]

