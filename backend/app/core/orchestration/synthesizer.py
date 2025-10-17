"""Response synthesizer for combining agent feedback."""
from typing import List, Dict, Any
from collections import Counter

from app.schemas.agent import AgentResponse, AgentSentiment
from app.schemas.feedback import FeedbackSynthesis


class ResponseSynthesizer:
    """Synthesizes feedback from multiple agents."""
    
    @staticmethod
    def synthesize(
        responses: List[AgentResponse],
        round_number: int,
    ) -> FeedbackSynthesis:
        """
        Synthesize feedback from multiple agent responses.
        
        Args:
            responses: List of agent responses
            round_number: Current round number
        
        Returns:
            FeedbackSynthesis with combined insights
        """
        if not responses:
            return FeedbackSynthesis(
                round_number=round_number,
                total_agents=0,
                consensus_insights=[],
                divergent_opinions=[],
                top_opportunities=[],
                top_concerns=[],
                priority_questions=[],
                next_steps_suggested=[],
                overall_sentiment=AgentSentiment.NEUTRAL,
                confidence_level="low",
            )
        
        # Identify consensus insights (mentioned by multiple agents)
        consensus = ResponseSynthesizer._find_consensus(responses)
        
        # Identify divergent opinions
        divergent = ResponseSynthesizer._find_divergent_opinions(responses)
        
        # Aggregate opportunities
        top_opportunities = ResponseSynthesizer._aggregate_items(
            [r.opportunities for r in responses],
            top_n=5,
        )
        
        # Aggregate concerns
        top_concerns = ResponseSynthesizer._aggregate_items(
            [r.concerns for r in responses],
            top_n=5,
        )
        
        # Aggregate questions
        priority_questions = ResponseSynthesizer._aggregate_items(
            [r.questions for r in responses],
            top_n=5,
        )
        
        # Aggregate recommendations as next steps
        next_steps = ResponseSynthesizer._aggregate_items(
            [r.recommendations for r in responses],
            top_n=6,
        )
        
        # Calculate overall sentiment
        overall_sentiment = ResponseSynthesizer._calculate_overall_sentiment(responses)
        
        # Calculate confidence level
        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
        confidence_level = ResponseSynthesizer._confidence_to_level(avg_confidence)
        
        return FeedbackSynthesis(
            round_number=round_number,
            total_agents=len(responses),
            consensus_insights=consensus,
            divergent_opinions=divergent,
            top_opportunities=top_opportunities,
            top_concerns=top_concerns,
            priority_questions=priority_questions,
            next_steps_suggested=next_steps,
            overall_sentiment=overall_sentiment,
            confidence_level=confidence_level,
        )
    
    @staticmethod
    def _find_consensus(responses: List[AgentResponse]) -> List[str]:
        """Find consensus insights mentioned by multiple agents."""
        # This is a simplified version - in production, you'd use NLP similarity
        consensus_items = []
        
        # Look for common themes in summaries
        summaries = [r.summary.lower() for r in responses]
        
        # Count sentiment agreement
        sentiment_counts = Counter(r.sentiment for r in responses)
        most_common_sentiment = sentiment_counts.most_common(1)[0]
        
        if most_common_sentiment[1] >= len(responses) * 0.6:  # 60% agreement
            consensus_items.append(
                f"{most_common_sentiment[1]} out of {len(responses)} experts are "
                f"{most_common_sentiment[0].value.replace('_', ' ')} about this idea"
            )
        
        # Look for common keywords in opportunities and concerns
        all_opportunities = ' '.join(
            ' '.join(r.opportunities) for r in responses
        ).lower()
        
        common_opportunity_terms = ['market', 'growth', 'demand', 'innovation', 'potential']
        for term in common_opportunity_terms:
            count = all_opportunities.count(term)
            if count >= len(responses) * 0.5:
                consensus_items.append(
                    f"Multiple experts highlight {term}-related opportunities"
                )
        
        return consensus_items[:5]  # Return top 5
    
    @staticmethod
    def _find_divergent_opinions(
        responses: List[AgentResponse]
    ) -> List[Dict[str, str]]:
        """Find areas where agents disagree."""
        divergent = []
        
        # Check sentiment divergence
        sentiments = [r.sentiment for r in responses]
        sentiment_set = set(sentiments)
        
        if len(sentiment_set) >= 3:  # Significant divergence
            # Group by sentiment
            positive = [r for r in responses if r.sentiment in [
                AgentSentiment.VERY_POSITIVE, AgentSentiment.POSITIVE
            ]]
            negative = [r for r in responses if r.sentiment in [
                AgentSentiment.NEGATIVE, AgentSentiment.CAUTIOUS
            ]]
            
            if positive and negative:
                divergent.append({
                    "topic": "Overall Assessment",
                    "viewpoint_a": f"{positive[0].agent_name} is optimistic: {positive[0].summary[:100]}...",
                    "viewpoint_b": f"{negative[0].agent_name} is cautious: {negative[0].summary[:100]}...",
                })
        
        return divergent
    
    @staticmethod
    def _aggregate_items(
        item_lists: List[List[str]],
        top_n: int = 5,
    ) -> List[str]:
        """Aggregate and rank items from multiple lists."""
        # Flatten all items
        all_items = []
        for items in item_lists:
            all_items.extend(items)
        
        # Simple deduplication and ranking by frequency
        item_counts = Counter(all_items)
        
        # Return most common items
        return [item for item, _ in item_counts.most_common(top_n)]
    
    @staticmethod
    def _calculate_overall_sentiment(
        responses: List[AgentResponse]
    ) -> AgentSentiment:
        """Calculate overall sentiment from agent responses."""
        sentiment_values = {
            AgentSentiment.VERY_POSITIVE: 2,
            AgentSentiment.POSITIVE: 1,
            AgentSentiment.NEUTRAL: 0,
            AgentSentiment.CAUTIOUS: -1,
            AgentSentiment.NEGATIVE: -2,
        }
        
        avg_value = sum(
            sentiment_values[r.sentiment] for r in responses
        ) / len(responses)
        
        # Map back to sentiment
        if avg_value >= 1.5:
            return AgentSentiment.VERY_POSITIVE
        elif avg_value >= 0.5:
            return AgentSentiment.POSITIVE
        elif avg_value > -0.5:
            return AgentSentiment.NEUTRAL
        elif avg_value > -1.5:
            return AgentSentiment.CAUTIOUS
        else:
            return AgentSentiment.NEGATIVE
    
    @staticmethod
    def _confidence_to_level(avg_confidence: float) -> str:
        """Convert average confidence score to level."""
        if avg_confidence >= 0.8:
            return "high"
        elif avg_confidence >= 0.6:
            return "medium"
        else:
            return "low"

