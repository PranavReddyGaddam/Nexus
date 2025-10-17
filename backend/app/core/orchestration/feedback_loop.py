"""Feedback loop manager for iterative refinement."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.core.agents.base_agent import BaseAgent
from app.core.orchestration.coordinator import MultiAgentCoordinator
from app.core.orchestration.synthesizer import ResponseSynthesizer
from app.schemas.research import StartupIdea
from app.schemas.agent import AgentResponse
from app.schemas.feedback import FeedbackRound, FeedbackRoundStatus, FeedbackSynthesis
from app.config import settings


class FeedbackLoopManager:
    """Manages iterative feedback loops with multiple agents."""
    
    def __init__(self, agents: List[BaseAgent]):
        """
        Initialize the feedback loop manager.
        
        Args:
            agents: List of agents to use in feedback loop
        """
        self.agents = agents
        self.coordinator = MultiAgentCoordinator(agents)
        self.synthesizer = ResponseSynthesizer()
        
        self.rounds: List[FeedbackRound] = []
        self.session_id: str = str(uuid.uuid4())
    
    async def execute_round(
        self,
        idea: StartupIdea,
        user_input: Optional[str] = None,
        mode: str = "parallel",
    ) -> FeedbackRound:
        """
        Execute a single feedback round.
        
        Args:
            idea: Startup idea to analyze
            user_input: Additional user input for this round
            mode: Execution mode ("parallel" or "sequential")
        
        Returns:
            FeedbackRound with all responses and synthesis
        """
        round_number = len(self.rounds) + 1
        round_id = str(uuid.uuid4())
        
        # Create feedback round
        feedback_round = FeedbackRound(
            round_id=round_id,
            session_id=self.session_id,
            round_number=round_number,
            status=FeedbackRoundStatus.IN_PROGRESS,
            user_input=user_input,
            agent_responses=[],
            synthesis=None,
            consensus_points=[],
            divergent_points=[],
            overall_sentiment=AgentSentiment.NEUTRAL,
            started_at=datetime.utcnow(),
            completed_at=None,
        )
        
        try:
            # Get previous responses if this isn't the first round
            previous_responses = None
            if round_number > 1:
                previous_responses = self.rounds[-1].agent_responses
            
            # Execute agents
            if mode == "sequential":
                responses = await self.coordinator.run_sequential_dialogue(
                    idea=idea,
                    round_number=round_number,
                    user_context=user_input,
                )
            else:  # parallel
                responses = await self.coordinator.run_parallel_analysis(
                    idea=idea,
                    round_number=round_number,
                    user_context=user_input,
                    previous_responses=previous_responses,
                )
            
            feedback_round.agent_responses = responses
            
            # Synthesize responses
            synthesis = self.synthesizer.synthesize(responses, round_number)
            feedback_round.synthesis = synthesis.model_dump_json()
            feedback_round.consensus_points = synthesis.consensus_insights
            feedback_round.divergent_points = [
                {"topic": d["topic"], "views": [d["viewpoint_a"], d["viewpoint_b"]]}
                for d in synthesis.divergent_opinions
            ]
            feedback_round.overall_sentiment = synthesis.overall_sentiment
            
            # Mark as completed
            feedback_round.status = FeedbackRoundStatus.COMPLETED
            feedback_round.completed_at = datetime.utcnow()
            
        except Exception as e:
            feedback_round.status = FeedbackRoundStatus.FAILED
            feedback_round.completed_at = datetime.utcnow()
            print(f"Feedback round failed: {str(e)}")
        
        # Store round
        self.rounds.append(feedback_round)
        
        return feedback_round
    
    async def run_multiple_rounds(
        self,
        idea: StartupIdea,
        num_rounds: int = 3,
        user_inputs: Optional[List[Optional[str]]] = None,
    ) -> List[FeedbackRound]:
        """
        Run multiple feedback rounds.
        
        Args:
            idea: Startup idea to analyze
            num_rounds: Number of rounds to execute
            user_inputs: Optional user inputs for each round
        
        Returns:
            List of completed feedback rounds
        """
        if user_inputs is None:
            user_inputs = [None] * num_rounds
        
        for i in range(num_rounds):
            user_input = user_inputs[i] if i < len(user_inputs) else None
            await self.execute_round(idea, user_input)
        
        return self.rounds
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire session."""
        if not self.rounds:
            return {}
        
        total_responses = sum(len(r.agent_responses) for r in self.rounds)
        
        # Aggregate all consensus points
        all_consensus = []
        for r in self.rounds:
            all_consensus.extend(r.consensus_points)
        
        # Get final sentiment
        final_sentiment = self.rounds[-1].overall_sentiment if self.rounds else None
        
        return {
            "session_id": self.session_id,
            "total_rounds": len(self.rounds),
            "total_agents": len(self.agents),
            "total_responses": total_responses,
            "key_insights": list(set(all_consensus))[:10],
            "final_sentiment": final_sentiment,
            "rounds": [
                {
                    "round_number": r.round_number,
                    "agent_count": len(r.agent_responses),
                    "sentiment": r.overall_sentiment,
                    "status": r.status,
                }
                for r in self.rounds
            ],
        }


# Import required for type hints
from app.schemas.agent import AgentSentiment

