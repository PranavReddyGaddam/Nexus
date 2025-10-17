from typing import Dict, Any
import json
from datetime import datetime
from services.openai_service import OpenAIService
from services.realtime_service import RealtimeService
from models.schemas import AnalysisResponse, AnalysisResults, Persona, Opinion, SentimentBreakdown

class AnalysisService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.realtime_service = RealtimeService()
    
    async def run_analysis(self, product_idea: str, session_id: int) -> AnalysisResponse:
        """
        Run complete analysis pipeline
        """
        try:
            # Send initial status update
            await self.realtime_service.broadcast_status(session_id, "processing", 10)
            
            # Validate input
            validated_input = self._validate_input(product_idea)
            if not validated_input["valid"]:
                await self.realtime_service.broadcast_error(session_id, validated_input["error"])
                raise ValueError(validated_input["error"])
            
            # Send progress update
            await self.realtime_service.broadcast_status(session_id, "processing", 30)
            
            # Call OpenAI for analysis
            ai_results = await self.openai_service.analyze_product_idea(product_idea)
            
            # Send progress update
            await self.realtime_service.broadcast_status(session_id, "processing", 70)
            
            # Format results
            formatted_results = self._format_analysis_results(ai_results)
            
            # Send progress update
            await self.realtime_service.broadcast_status(session_id, "processing", 90)
            
            # Create final response
            analysis_response = AnalysisResponse(
                session_id=session_id,
                product_idea=product_idea,
                analysis_results=formatted_results,
                metadata={
                    "processed_at": datetime.now().isoformat(),
                    "processing_time": "45 seconds",
                    "confidence_score": self._calculate_confidence_score(ai_results),
                    "data_quality": self._assess_data_quality(ai_results)
                },
                status="completed"
            )
            
            # Send completion update
            await self.realtime_service.broadcast_results(session_id, analysis_response.dict())
            
            return analysis_response
            
        except Exception as e:
            # Send error update
            await self.realtime_service.broadcast_error(session_id, str(e))
            raise e
    
    def _validate_input(self, product_idea: str) -> Dict[str, Any]:
        """Validate product idea input"""
        if not product_idea or not product_idea.strip():
            return {"valid": False, "error": "Product idea cannot be empty"}
        
        if len(product_idea.strip()) < 10:
            return {"valid": False, "error": "Product idea too short (minimum 10 characters)"}
        
        if len(product_idea.strip()) > 500:
            return {"valid": False, "error": "Product idea too long (maximum 500 characters)"}
        
        return {"valid": True}
    
    def _format_analysis_results(self, ai_results: Dict[str, Any]) -> AnalysisResults:
        """Format AI results into structured response"""
        # Convert personas
        personas = []
        for persona_data in ai_results.get("personas", []):
            personas.append(Persona(**persona_data))
        
        # Convert opinions
        opinions = []
        for opinion_data in ai_results.get("opinions", []):
            opinions.append(Opinion(**opinion_data))
        
        # Convert sentiment breakdown
        sentiment_data = ai_results.get("sentiment_breakdown", {})
        sentiment_breakdown = SentimentBreakdown(**sentiment_data)
        
        return AnalysisResults(
            personas=personas,
            opinions=opinions,
            summary=ai_results.get("summary", ""),
            sentiment_breakdown=sentiment_breakdown,
            market_potential=ai_results.get("market_potential", "unknown"),
            key_insights=ai_results.get("key_insights", []),
            recommendations=ai_results.get("recommendations", [])
        )
    
    def _calculate_confidence_score(self, ai_results: Dict[str, Any]) -> int:
        """Calculate confidence score for analysis"""
        score = 0
        
        if ai_results.get("personas"):
            score += 30
        if ai_results.get("opinions"):
            score += 30
        if ai_results.get("summary"):
            score += 20
        if len(ai_results.get("opinions", [])) >= 3:
            score += 20
        
        return min(score, 100)
    
    def _assess_data_quality(self, ai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of generated data"""
        quality_indicators = []
        
        if ai_results.get("personas") and len(ai_results.get("personas", [])) >= 3:
            quality_indicators.append("sufficient_personas")
        
        if ai_results.get("opinions") and len(ai_results.get("opinions", [])) >= 3:
            quality_indicators.append("sufficient_opinions")
        
        if ai_results.get("summary") and len(ai_results.get("summary", "")) > 50:
            quality_indicators.append("detailed_summary")
        
        return {
            "score": len(quality_indicators) / 3 * 100,
            "indicators": quality_indicators
        }
