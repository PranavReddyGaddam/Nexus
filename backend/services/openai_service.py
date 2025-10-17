import openai
from typing import Dict, Any, List
import json
import re
from config.settings import settings

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def analyze_product_idea(self, product_idea: str) -> Dict[str, Any]:
        """
        Analyze product idea using OpenAI and return structured data
        """
        try:
            # Create the prompt
            prompt = self._create_analysis_prompt(product_idea)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a market research AI assistant specializing in persona analysis and product validation. Be thorough, realistic, and data-driven in your analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract the response content
            raw_response = response.choices[0].message.content
            
            # Parse the response into structured data
            structured_data = self._parse_ai_response(raw_response)
            
            return structured_data
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Return fallback data for demo purposes
            return self._get_fallback_data(product_idea)
    
    def _create_analysis_prompt(self, product_idea: str) -> str:
        """Create the analysis prompt for OpenAI"""
        return f"""
Analyze this product idea: "{product_idea}"

Please provide a comprehensive market analysis with the following structure:

**PERSONAS (3-5 personas):**
For each persona, include:
- Name and age
- Location and occupation
- Brief background
- Their perspective on this product idea

**OPINIONS:**
For each persona, provide their specific opinion including:
- What they like about the idea
- What concerns they have
- How likely they are to use/purchase it
- Any suggestions for improvement

**SUMMARY:**
Provide a 2-3 sentence summary of the overall market reception, key opportunities, and main challenges.

Format your response exactly like this:

Persona 1: [Name], [Age], [Location], [Occupation]
Background: [Brief description]
Opinion: [Detailed opinion with specific feedback]

Persona 2: [Name], [Age], [Location], [Occupation]
Background: [Brief description]
Opinion: [Detailed opinion with specific feedback]

[Continue for 3-5 personas]

Summary: [Overall market assessment]
"""
    
    def _parse_ai_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse OpenAI response into structured data"""
        try:
            # Extract personas
            personas = self._extract_personas(raw_response)
            
            # Extract opinions
            opinions = self._extract_opinions(raw_response)
            
            # Extract summary
            summary = self._extract_summary(raw_response)
            
            # Calculate sentiment breakdown
            sentiment_breakdown = self._calculate_sentiment_breakdown(opinions)
            
            # Assess market potential
            market_potential = self._assess_market_potential(opinions)
            
            # Generate key insights and recommendations
            key_insights = self._generate_key_insights(personas, opinions)
            recommendations = self._generate_recommendations(opinions, market_potential)
            
            return {
                "personas": personas,
                "opinions": opinions,
                "summary": summary,
                "sentiment_breakdown": sentiment_breakdown,
                "market_potential": market_potential,
                "key_insights": key_insights,
                "recommendations": recommendations,
                "raw_response": raw_response
            }
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._get_fallback_data("")
    
    def _extract_personas(self, text: str) -> List[Dict[str, Any]]:
        """Extract persona information from AI response"""
        personas = []
        persona_pattern = r"Persona \d+: ([^,]+), (\d+), ([^,]+), ([^\n]+)\nBackground: ([^\n]+)"
        
        matches = re.findall(persona_pattern, text)
        
        for i, match in enumerate(matches):
            personas.append({
                "id": i + 1,
                "name": match[0].strip(),
                "age": int(match[1]),
                "location": match[2].strip(),
                "occupation": match[3].strip(),
                "description": match[4].strip()
            })
        
        # If no personas found, create default ones
        if not personas:
            personas = [
                {
                    "id": 1,
                    "name": "Tech-Savvy Professional",
                    "age": 35,
                    "location": "Urban",
                    "occupation": "Marketing Manager",
                    "description": "Tech-savvy professional looking for innovative solutions"
                },
                {
                    "id": 2,
                    "name": "Budget-Conscious Consumer",
                    "age": 42,
                    "location": "Suburban",
                    "occupation": "Software Engineer",
                    "description": "Value-conscious consumer who researches before purchasing"
                }
            ]
        
        return personas
    
    def _extract_opinions(self, text: str) -> List[Dict[str, Any]]:
        """Extract opinions from AI response"""
        opinions = []
        opinion_pattern = r"Opinion: ([^\n]+)"
        
        matches = re.findall(opinion_pattern, text)
        
        for i, match in enumerate(matches):
            opinions.append({
                "id": i + 1,
                "persona_id": (i % 3) + 1,  # Distribute across personas
                "content": match.strip(),
                "sentiment": self._analyze_sentiment(match)
            })
        
        return opinions
    
    def _extract_summary(self, text: str) -> str:
        """Extract summary from AI response"""
        summary_pattern = r"Summary: ([^\n]+)"
        match = re.search(summary_pattern, text)
        
        if match:
            return match.group(1).strip()
        else:
            return "Analysis completed successfully. The product shows potential with mixed market reception."
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ["like", "love", "great", "good", "excellent", "amazing", "positive", "promising"]
        negative_words = ["hate", "bad", "terrible", "awful", "dislike", "concern", "worry", "negative"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_sentiment_breakdown(self, opinions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate sentiment distribution"""
        sentiments = [opinion.get("sentiment", "neutral") for opinion in opinions]
        
        return {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral"),
            "total": len(sentiments)
        }
    
    def _assess_market_potential(self, opinions: List[Dict[str, Any]]) -> str:
        """Assess market potential based on opinions"""
        if not opinions:
            return "unknown"
        
        positive_count = sum(1 for op in opinions if op.get("sentiment") == "positive")
        total_count = len(opinions)
        positive_ratio = positive_count / total_count
        
        if positive_ratio >= 0.7:
            return "high"
        elif positive_ratio >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _generate_key_insights(self, personas: List[Dict[str, Any]], opinions: List[Dict[str, Any]]) -> List[str]:
        """Generate key insights"""
        insights = []
        
        if personas:
            insights.append(f"Analyzed {len(personas)} target personas")
        
        if opinions:
            insights.append(f"Generated {len(opinions)} detailed opinions")
        
        insights.append("Market analysis completed successfully")
        
        return insights
    
    def _generate_recommendations(self, opinions: List[Dict[str, Any]], market_potential: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if market_potential == "high":
            recommendations.append("Strong market reception - consider proceeding with development")
        elif market_potential == "medium":
            recommendations.append("Mixed reception - consider addressing concerns before launch")
        else:
            recommendations.append("Low market reception - significant product iteration needed")
        
        recommendations.append("Conduct additional user research to validate findings")
        recommendations.append("Develop targeted marketing strategy based on persona analysis")
        
        return recommendations
    
    def _get_fallback_data(self, product_idea: str) -> Dict[str, Any]:
        """Fallback data if OpenAI fails"""
        return {
            "personas": [
                {
                    "id": 1,
                    "name": "Sarah",
                    "age": 35,
                    "location": "Toronto",
                    "occupation": "Marketing Manager",
                    "description": "Tech-savvy professional looking for innovative solutions"
                },
                {
                    "id": 2,
                    "name": "Mike",
                    "age": 42,
                    "location": "Vancouver",
                    "occupation": "Software Engineer",
                    "description": "Security-conscious professional who researches before purchasing"
                },
                {
                    "id": 3,
                    "name": "Emma",
                    "age": 38,
                    "location": "Montreal",
                    "occupation": "Financial Advisor",
                    "description": "Financial professional who understands consumer needs"
                }
            ],
            "opinions": [
                {
                    "id": 1,
                    "persona_id": 1,
                    "content": "I like the focus on my generation, there's definitely a gap in the market for innovative financial solutions",
                    "sentiment": "positive"
                },
                {
                    "id": 2,
                    "persona_id": 2,
                    "content": "While the concept is interesting, I have concerns about security and data privacy",
                    "sentiment": "neutral"
                },
                {
                    "id": 3,
                    "persona_id": 3,
                    "content": "This could really help with financial planning for our demographic",
                    "sentiment": "positive"
                }
            ],
            "summary": "Mixed reception with positive overall sentiment. Key focus areas include security, trust-building, and addressing specific generational needs.",
            "sentiment_breakdown": {
                "positive": 2,
                "negative": 0,
                "neutral": 1,
                "total": 3
            },
            "market_potential": "medium",
            "key_insights": [
                "Analyzed 3 target personas",
                "Generated 3 detailed opinions",
                "Market analysis completed successfully"
            ],
            "recommendations": [
                "Mixed reception - consider addressing security concerns before launch",
                "Conduct additional user research to validate findings",
                "Develop targeted marketing strategy based on persona analysis"
            ],
            "raw_response": "Fallback data used due to API error"
        }
