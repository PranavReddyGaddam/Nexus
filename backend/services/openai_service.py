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

    async def rank_product_idea(self, idea: str, personas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Rank product idea using OpenAI with structured evaluation system using predefined personas
        """
        try:
            # Create the ranking prompt with specific personas
            prompt = self._create_ranking_prompt(idea, personas)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert product evaluator specializing in market research and persona analysis. Provide detailed, structured evaluations with numerical ratings and relevance scores. Use only plain text formatting - no asterisks, dashes, or markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            # Extract the response content
            raw_response = response.choices[0].message.content
            
            # Parse the response into structured ranking data
            structured_data = self._parse_ranking_response(raw_response, idea, personas)
            
            return structured_data
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Return fallback ranking data
            return self._get_fallback_ranking_data(idea, personas)
    
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

    def _create_ranking_prompt(self, idea: str, personas: List[Dict[str, Any]]) -> str:
        """Create the ranking prompt for OpenAI using predefined personas"""
        persona_list = "\n".join([
            f"- {p['name']} ({p['title']}, {p['location']}, {p['industry']}) - Expertise: {', '.join(p['expertise'])}"
            for p in personas
        ])
        
        return f"""
Analyze and rank this product idea: "{idea}"

You will evaluate this idea from the perspective of these specific personas:

{persona_list}

For each persona, provide a detailed evaluation in this exact format:

ENHANCED IDEA: [Enhanced version of the original idea with specific details, target market, and value proposition]

PERSONA EVALUATIONS:

Persona: {personas[0]['name']}
Title: {personas[0]['title']}
Location: {personas[0]['location']}
Industry: {personas[0]['industry']}
Expertise: {', '.join(personas[0]['expertise'])}
Experience: {personas[0]['experience']}
Relevance Score: [0.0-1.0]
Rating: [1-10]
Sentiment: [positive/neutral/negative]
Key Insight: [Most important insight from this persona's perspective]
Detailed Analysis: [Comprehensive explanation of why they think it's good/bad, including specific reasoning based on their expertise and experience]

Persona: {personas[1]['name']}
Title: {personas[1]['title']}
Location: {personas[1]['location']}
Industry: {personas[1]['industry']}
Expertise: {', '.join(personas[1]['expertise'])}
Experience: {personas[1]['experience']}
Relevance Score: [0.0-1.0]
Rating: [1-10]
Sentiment: [positive/neutral/negative]
Key Insight: [Most important insight from this persona's perspective]
Detailed Analysis: [Comprehensive explanation of why they think it's good/bad, including specific reasoning based on their expertise and experience]

[Continue for all personas]

SUMMARY:
Average Rating: [X.X]
Overall Sentiment: [positive/neutral/negative]
Top Concerns: [List 3-5 main concerns raised]
Top Opportunities: [List 3-5 main opportunities identified]

IMPORTANT: Do not use asterisks, dashes, or markdown formatting. Use plain text only.
"""

    def _parse_ranking_response(self, raw_response: str, original_idea: str, personas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse OpenAI ranking response into structured data"""
        try:
            # Extract enhanced idea
            enhanced_idea = self._extract_enhanced_idea(raw_response, original_idea)
            
            # Extract persona evaluations
            persona_evaluations = self._extract_persona_evaluations_structured(raw_response, personas)
            
            # Extract summary
            summary = self._extract_ranking_summary(raw_response)
            
            return {
                "enhanced_idea": enhanced_idea,
                "results": persona_evaluations,
                "summary": summary,
                "raw_response": raw_response
            }
            
        except Exception as e:
            print(f"Error parsing ranking response: {e}")
            return self._get_fallback_ranking_data(original_idea, personas)

    def _extract_enhanced_idea(self, text: str, original_idea: str) -> str:
        """Extract enhanced idea from response"""
        enhanced_pattern = r"ENHANCED IDEA:\s*([^\n]+)"
        match = re.search(enhanced_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        else:
            return f"Enhanced version of: {original_idea}"

    def _extract_persona_evaluations_structured(self, text: str, personas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract persona evaluations from structured response using predefined personas"""
        evaluations = []
        
        # Split by "Persona:" sections
        persona_sections = re.split(r'Persona:', text)
        
        for i, section in enumerate(persona_sections[1:], 0):  # Skip first empty section
            if i >= len(personas):
                break
                
            try:
                persona = personas[i]
                lines = section.strip().split('\n')
                
                # Extract fields from the structured format
                relevance_score = float(self._extract_field_value(lines, "Relevance Score:", "0.8"))
                rating = int(self._extract_field_value(lines, "Rating:", "7"))
                sentiment = self._extract_field_value(lines, "Sentiment:", "neutral")
                key_insight = self._extract_field_value(lines, "Key Insight:", "Product shows potential")
                detailed_analysis = self._extract_field_value(lines, "Detailed Analysis:", "Detailed analysis of market fit")
                
                evaluations.append({
                    "persona": {
                        "id": persona["id"],
                        "name": persona["name"],
                        "title": persona["title"],
                        "location": persona["location"],
                        "industry": persona["industry"],
                        "expertise": persona["expertise"],
                        "experience": persona["experience"]
                    },
                    "relevanceScore": relevance_score,
                    "rating": rating,
                    "sentiment": sentiment,
                    "keyInsight": key_insight,
                    "reason": detailed_analysis
                })
                
            except Exception as e:
                print(f"Error parsing persona {i}: {e}")
                continue
        
        # If no evaluations found, create fallback using provided personas
        if not evaluations:
            evaluations = self._create_fallback_evaluations_from_personas(personas)
        
        return evaluations

    def _extract_field_value(self, lines: List[str], field_name: str, default: str) -> str:
        """Extract value for a specific field from lines"""
        for line in lines:
            if field_name in line:
                return line.split(field_name, 1)[1].strip()
        return default

    def _extract_ranking_summary(self, text: str) -> Dict[str, Any]:
        """Extract ranking summary from response"""
        summary_pattern = r"SUMMARY:\s*\nAverage Rating:\s*([0-9.]+)\s*\nOverall Sentiment:\s*(\w+)\s*\nTop Concerns:\s*([^\n]+)\s*\nTop Opportunities:\s*([^\n]+)"
        match = re.search(summary_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            return {
                "averageRating": float(match.group(1)),
                "overallSentiment": match.group(2).lower(),
                "topConcerns": [concern.strip() for concern in match.group(3).split(',')],
                "topOpportunities": [opp.strip() for opp in match.group(4).split(',')]
            }
        else:
            return {
                "averageRating": 7.0,
                "overallSentiment": "neutral",
                "topConcerns": ["Market competition", "Implementation complexity", "User adoption"],
                "topOpportunities": ["Strong market demand", "Innovative approach", "Scalable model"]
            }

    def _create_default_persona_evaluations(self) -> List[Dict[str, Any]]:
        """Create default persona evaluations"""
        return [
            {
                "persona": {
                    "id": "1",
                    "name": "Sarah",
                    "title": "Marketing Director",
                    "location": "San Francisco",
                    "industry": "Tech",
                    "expertise": ["Digital marketing", "Consumer behavior"],
                    "experience": "8 years"
                },
                "relevanceScore": 0.9,
                "rating": 8,
                "sentiment": "positive",
                "keyInsight": "Strong market demand for this solution",
                "reason": "Addresses clear pain point with innovative approach"
            },
            {
                "persona": {
                    "id": "2",
                    "name": "Mike",
                    "title": "Product Manager",
                    "location": "New York",
                    "industry": "Finance",
                    "expertise": ["Product strategy", "User research"],
                    "experience": "6 years"
                },
                "relevanceScore": 0.8,
                "rating": 7,
                "sentiment": "neutral",
                "keyInsight": "Good concept but needs refinement",
                "reason": "Solid foundation but execution details unclear"
            }
        ]

    def _create_fallback_evaluations_from_personas(self, personas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create fallback evaluations using provided personas"""
        evaluations = []
        for i, persona in enumerate(personas):
            evaluations.append({
                "persona": {
                    "id": persona["id"],
                    "name": persona["name"],
                    "title": persona["title"],
                    "location": persona["location"],
                    "industry": persona["industry"],
                    "expertise": persona["expertise"],
                    "experience": persona["experience"]
                },
                "relevanceScore": 0.8,
                "rating": 7,
                "sentiment": "neutral",
                "keyInsight": f"Based on {persona['experience']} in {persona['industry']}, this idea shows potential.",
                "reason": f"As a {persona['title']} with expertise in {', '.join(persona['expertise'][:2])}, I see both opportunities and challenges with this concept. The market shows interest in this type of solution, but execution and differentiation will be key factors for success."
            })
        return evaluations

    def _get_fallback_ranking_data(self, idea: str, personas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback ranking data if OpenAI fails"""
        return {
            "enhanced_idea": f"Enhanced version of: {idea}",
            "results": self._create_fallback_evaluations_from_personas(personas),
            "summary": {
                "averageRating": 7.0,
                "overallSentiment": "neutral",
                "topConcerns": ["Market competition", "Implementation complexity"],
                "topOpportunities": ["Strong market demand", "Innovative approach"]
            },
            "raw_response": "Fallback ranking data used due to API error"
        }
