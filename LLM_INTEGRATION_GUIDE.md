# LLM Integration Guide for Nexus

## 🎯 Overview

The Nexus platform now has a **complete structure for LLM integration** to intelligently select expert personas and generate ratings for startup ideas.

## 📁 Architecture

```
Frontend (React)
    ↓
analysisService.ts (handles LLM toggle)
    ↓
Backend API (/api/v1/research/analyze-idea)
    ↓
LLM Provider (OpenAI/Anthropic)
    ↓
Structured Response with Persona Ratings
```

## 🔧 Current State

### ✅ What's Implemented

1. **Frontend Service Layer** (`frontend/src/services/analysisService.ts`)
   - Mock analysis (randomized, currently active)
   - LLM analysis placeholder (ready for backend integration)
   - Toggle between mock and real LLM
   - Proper TypeScript types

2. **Backend API Endpoint** (`backend/app/api/v1/analyze.py`)
   - POST `/api/v1/research/analyze-idea`
   - LLM-powered persona selection
   - Rating generation from expert perspectives
   - Structured JSON response

3. **Integration Points**
   - App.tsx uses the service layer
   - Ready to flip `LLM_CONFIG.enabled` to `true`
   - Proper error handling and fallbacks

## 🚀 How to Enable LLM

### Step 1: Backend Setup

1. **Ensure your backend is running:**
```bash
cd backend
export OPENAI_API_KEY="your-key-here"  # or ANTHROPIC_API_KEY
export LLM_PROVIDER="openai"  # or "anthropic"
python -m app.main
```

2. **Test the endpoint:**
```bash
curl -X POST http://localhost:8000/api/v1/research/analyze-idea \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "An AI-powered fitness app that creates personalized workout plans",
    "max_agents": 5
  }'
```

### Step 2: Frontend Configuration

1. **Create `.env` file in frontend:**
```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

2. **Enable LLM in the service:**

Edit `frontend/src/services/analysisService.ts`:

```typescript
export const LLM_CONFIG = {
  enabled: true,  // ← Change this to true
  apiUrl: 'http://localhost:8000/api/v1',
  timeout: 30000,
  maxRetries: 2,
};
```

3. **Rebuild frontend:**
```bash
cd frontend
npm run dev
```

### Step 3: Test End-to-End

1. Go to http://localhost:5173/explore
2. Type a startup idea
3. Press Enter
4. Watch the console logs:
   - Should show `usingLLM: true`
   - Should show actual LLM-selected personas
   - Ratings should be based on AI analysis

## 📊 How It Works

### Frontend Flow

```typescript
// User submits idea
handleAnalyzeIdea("AI fitness app") 
    ↓
analyzeStartupIdea(personas, {
  idea: "AI fitness app",
  maxPersonas: 5,
  useRealLLM: true  // ← Uses LLM if enabled
})
    ↓
// If LLM enabled:
fetch('/api/v1/research/analyze-idea', {
  method: 'POST',
  body: JSON.stringify({ idea, max_agents })
})
    ↓
// If LLM disabled or fails:
mockAnalysis() // Randomized fallback
```

### Backend Flow

```python
# Endpoint receives request
@router.post("/analyze-idea")
async def analyze_startup_idea(request):
    ↓
# Get all available personas
available_personas = get_all_personas()
    ↓
# Call LLM with structured prompt
select_and_rate_personas_with_llm(
  idea,
  available_personas,
  max_agents
)
    ↓
# LLM analyzes and returns:
{
  "selected_experts": [
    {
      "persona_id": "ny-1",
      "rating": 8.5,
      "sentiment": "positive",
      "key_insight": "Strong market fit...",
      "relevance_score": 0.95,
      "reasoning": "VC expert relevant for..."
    }
  ]
}
    ↓
# Return structured response to frontend
```

## 🎨 LLM Prompt Structure

The backend sends this to the LLM:

```
System Prompt:
"You are an expert business analyst who helps evaluate startup ideas..."

User Prompt:
"Startup Idea: [user's idea]

Available Experts:
1. Sarah Mitchell (ny-1)
   Industry: Finance & Investment
   Expertise: Venture Capital, Startup Valuation...
   Location: New York, USA

2. Marcus Chen (ny-2)
   ...

Please select up to 5 most relevant experts and provide their analysis.

Respond in JSON format:
{
  "selected_experts": [...]
}"
```

The LLM:
1. ✅ Analyzes which experts are most relevant
2. ✅ Rates the idea from each expert's perspective (0-10)
3. ✅ Determines sentiment (positive/neutral/cautious)
4. ✅ Generates insights specific to that expert's domain
5. ✅ Explains why each expert was selected

## 🔄 Switching Between Mock and LLM

### During Development

**Use Mock (current state):**
```typescript
// analysisService.ts
export const LLM_CONFIG = {
  enabled: false,  // Fast, no API costs
  ...
};
```

**Use Real LLM (when testing):**
```typescript
export const LLM_CONFIG = {
  enabled: true,  // Real AI analysis
  ...
};
```

### In Production

You can even let users toggle:

```typescript
// Add a toggle in the UI
const [useAI, setUseAI] = useState(true);

// Pass to analysis
analyzeStartupIdea(personas, {
  idea,
  useRealLLM: useAI,
});
```

## 🐛 Troubleshooting

### LLM Returns Invalid JSON

The backend handles this:
```python
# It tries to extract JSON from markdown
if "```json" in response_text:
    json_str = response_text.split("```json")[1]...
```

### API Call Fails

Automatic fallback:
```typescript
try {
  // Try LLM
  return await llmAnalysis(...);
} catch (error) {
  // Fall back to mock
  return mockAnalysis(...);
}
```

### Backend Not Running

Frontend shows error in console but doesn't crash:
```typescript
catch (error) {
  console.error("Analysis failed:", error);
  // UI continues to work
}
```

## 📈 Monitoring & Debugging

### Frontend Console Logs

```javascript
console.log("Analysis complete:", {
  idea,
  personasSelected: ["Sarah Mitchell", "Marcus Chen"],
  averageRating: 8.2,
  sentiment: "positive",
  usingLLM: true,  // ← Shows if LLM was used
});
```

### Backend Logs

Add to `analyze.py`:
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Analyzing idea: {idea}")
logger.info(f"LLM selected {len(results)} experts")
logger.info(f"Average rating: {avg_rating}")
```

## 🎯 Next Steps

### 1. Enhance the LLM Prompt

Add more context:
```python
user_prompt = f"""Startup Idea: "{idea}"

Industry Context:
- Current market trends
- Competitive landscape
- Regulatory environment

Available Experts:
...
"""
```

### 2. Add Multi-Round Analysis

User refines idea → LLM re-analyzes with context:
```python
previous_feedback: Optional[List[Dict]] = None
# Include in prompt
```

### 3. Add Caching

Cache LLM responses for common ideas:
```python
@lru_cache(maxsize=100)
async def cached_llm_analysis(...):
    ...
```

### 4. Add Streaming

Stream LLM response in real-time:
```python
async def llm_analysis_stream(...):
    async for chunk in llm.generate_stream(...):
        yield chunk
```

## 💰 Cost Estimation

### OpenAI GPT-4

- ~500 tokens per request (input + output)
- ~$0.01 per analysis
- 100 analyses = $1

### Anthropic Claude

- Similar token usage
- ~$0.008 per analysis
- 100 analyses = $0.80

### Recommendation

Start with mock for development, use LLM for production/demos.

## ✅ Checklist for Going Live

- [ ] Backend running with API key set
- [ ] Frontend .env configured
- [ ] `LLM_CONFIG.enabled = true`
- [ ] Test with 3-5 different startup ideas
- [ ] Check console logs show `usingLLM: true`
- [ ] Verify ratings make sense for each idea
- [ ] Monitor API costs
- [ ] Add error handling for rate limits
- [ ] Consider caching for common queries

## 🎓 Example Response

**Input:** "An AI-powered fitness app"

**LLM Selects:**
1. Marcus Chen (Tech strategist) - 8.5/10
2. Yuki Tanaka (IoT/Hardware) - 7.0/10
3. Priya Sharma (Market analyst) - 8.0/10

**Mock Selects:**
Random 5 personas with random ratings

**Key Difference:**
- LLM: Relevant experts, thoughtful ratings
- Mock: Random experts, random ratings

---

**You're all set!** 🚀

The infrastructure is ready. Just flip `enabled: true` when you want to use real AI.

