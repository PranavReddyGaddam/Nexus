import asyncio
import httpx
import json


BASE_URL = "http://127.0.0.1:8000"


async def test_ranking_endpoint(idea: str = "AI-powered personal finance copilot") -> None:
    async with httpx.AsyncClient(timeout=60) as client:
        # Test the new ranking endpoint
        resp = await client.post(
            f"{BASE_URL}/api/rank",
            json={
                "idea": idea,
                "max_personas": 5
            },
        )
        resp.raise_for_status()
        data = resp.json()
        
        print("=== RANKING ANALYSIS RESULTS ===")
        print(f"Enhanced Idea: {data['enhancedIdea']}")
        print(f"\nAverage Rating: {data['summary']['averageRating']}")
        print(f"Overall Sentiment: {data['summary']['overallSentiment']}")
        print(f"Top Concerns: {', '.join(data['summary']['topConcerns'])}")
        print(f"Top Opportunities: {', '.join(data['summary']['topOpportunities'])}")
        
        print(f"\n=== PERSONA EVALUATIONS ({len(data['results'])} personas) ===")
        for i, result in enumerate(data['results'], 1):
            persona = result['persona']
            print(f"\nPersona {i}: {persona['name']} - {persona['title']}")
            print(f"  Location: {persona['location']}, Industry: {persona['industry']}")
            print(f"  Expertise: {', '.join(persona['expertise'])}")
            print(f"  Experience: {persona['experience']}")
            print(f"  Relevance Score: {result['relevanceScore']}")
            print(f"  Rating: {result['rating']}/10")
            print(f"  Sentiment: {result['sentiment']}")
            print(f"  Key Insight: {result['keyInsight']}")
            print(f"  Reason: {result['reason']}")


if __name__ == "__main__":
    asyncio.run(test_ranking_endpoint())
