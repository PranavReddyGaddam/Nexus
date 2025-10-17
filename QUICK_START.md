# 🚀 Nexus Quick Start Guide

## What You Have Now

### ✅ Frontend
- Interactive 3D globe with 14 clickable locations
- 15 expert personas with detailed profiles
- Beautiful modal system
- Modern UI with animations

### ✅ Backend
- Complete multi-agent system
- REST API with 15+ endpoints
- LLM integration (OpenAI/Anthropic)
- Orchestration and synthesis
- WebSocket support

## Test It Right Now (5 Minutes)

### Step 1: Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

**What to test:**
- ✅ Click "Explore Nexus" button
- ✅ Click on any blue dot on the globe
- ✅ See persona modal appear
- ✅ Review expert profiles

### Step 2: Start the Backend

```bash
cd backend

# Create virtual environment (one time)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (one time)
pip install -r requirements.txt

# Set your API key
export OPENAI_API_KEY="your-key-here"
# OR
export ANTHROPIC_API_KEY="your-key-here"

export LLM_PROVIDER="openai"  # or "anthropic"

# Run the server
python -m app.main
```

Open http://localhost:8000/api/v1/docs in your browser.

**What to test:**
1. Go to `/personas` endpoint and click "Try it out" → "Execute"
2. See all 15 expert personas
3. Go to `/research/sessions` and create a test session:

```json
{
  "idea": {
    "title": "AI-Powered Fitness Coach",
    "description": "An mobile app that uses AI to create personalized workout plans based on user goals, fitness level, and available equipment.",
    "target_market": "United States, fitness enthusiasts aged 25-45",
    "industry": "Health & Fitness",
    "business_model": "Subscription-based ($9.99/month)",
    "technology_stack": ["React Native", "Python", "OpenAI", "AWS"],
    "stage": "ideation"
  },
  "auto_select_agents": true,
  "max_agents": 5
}
```

4. Copy the `session_id` from the response
5. Start a feedback round using the session_id
6. Watch as 5 expert agents analyze your idea!

## Example API Test (Using curl)

```bash
# 1. List all personas
curl http://localhost:8000/api/v1/personas

# 2. Get a specific persona
curl http://localhost:8000/api/v1/personas/ny-1

# 3. Create a research session
curl -X POST http://localhost:8000/api/v1/research/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "idea": {
      "title": "Sustainable Fashion Marketplace",
      "description": "A platform connecting eco-conscious consumers with sustainable fashion brands.",
      "target_market": "Europe and North America",
      "industry": "E-commerce & Fashion",
      "business_model": "Commission on sales",
      "stage": "ideation"
    },
    "auto_select_agents": true,
    "max_agents": 4
  }'

# 4. Start a feedback round (replace SESSION_ID)
curl -X POST http://localhost:8000/api/v1/research/sessions/SESSION_ID/rounds \
  -H "Content-Type: application/json" \
  -d '{"user_message": null}'
```

## Next Steps After Testing

### 1. Connect Frontend to Backend

Create `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function createResearchSession(idea: StartupIdea) {
  const response = await fetch(`${API_BASE_URL}/research/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      idea,
      auto_select_agents: true,
      max_agents: 5,
    }),
  });
  return response.json();
}

export async function startFeedbackRound(sessionId: string, userMessage?: string) {
  const response = await fetch(
    `${API_BASE_URL}/research/sessions/${sessionId}/rounds`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_message: userMessage }),
    }
  );
  return response.json();
}
```

### 2. Add Database (PostgreSQL)

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql

# Create database
createdb nexus_dev

# Update backend/.env
DATABASE_URL=postgresql://your_user:password@localhost:5432/nexus_dev

# Run migrations (when implemented)
alembic upgrade head
```

### 3. Add Redis (Optional, for caching)

```bash
# Install Redis
# macOS: brew install redis
# Ubuntu: sudo apt install redis

# Start Redis
redis-server

# Update backend/.env
REDIS_URL=redis://localhost:6379/0
```

### 4. Production Deployment

**Frontend:**
```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel, Netlify, or AWS S3
```

**Backend:**
```bash
cd backend
# Use Docker
docker build -t nexus-backend .
docker run -p 8000:8000 nexus-backend

# Or deploy to:
# - AWS EC2 / ECS
# - Google Cloud Run
# - Heroku
# - Railway
# - Render
```

## Troubleshooting

### Backend won't start
- ✅ Check Python version: `python --version` (need 3.11+)
- ✅ Verify API key is set: `echo $OPENAI_API_KEY`
- ✅ Check all dependencies installed: `pip list`

### Frontend won't build
- ✅ Check Node version: `node --version` (need 16+)
- ✅ Clear node_modules: `rm -rf node_modules && npm install`
- ✅ Clear cache: `npm cache clean --force`

### LLM responses failing
- ✅ Verify API key is valid
- ✅ Check API quota/credits
- ✅ Try the other provider (OpenAI ↔ Anthropic)

### CORS errors
- ✅ Backend is configured for localhost:5173 and localhost:3000
- ✅ If using different port, update `backend/app/config.py`

## Understanding the Flow

```
1. User submits startup idea
   ↓
2. System auto-selects 3-7 relevant expert agents
   ↓
3. Agents analyze in parallel using LLM
   ↓
4. System synthesizes all feedback
   ↓
5. User sees consensus, opportunities, concerns
   ↓
6. User refines idea based on feedback
   ↓
7. Next round: Agents review refinements
   ↓
8. Iterate until satisfied
   ↓
9. Generate final report with recommendations
```

## Key Files to Understand

**Frontend:**
- `src/App.tsx` - Main app with routing and globe
- `src/components/PersonaModal.tsx` - Persona display
- `src/components/ui/globe.tsx` - 3D globe component
- `src/data/personas.ts` - Expert persona data

**Backend:**
- `app/main.py` - FastAPI app entry point
- `app/core/agents/base_agent.py` - Agent implementation
- `app/core/orchestration/coordinator.py` - Multi-agent coordination
- `app/core/orchestration/synthesizer.py` - Response synthesis
- `app/api/v1/research.py` - Main API endpoints
- `app/data/personas.py` - Persona data matching frontend

## Feature Checklist

### Implemented ✅
- [x] Interactive 3D globe
- [x] Clickable location pinpoints
- [x] Persona modal system
- [x] 15 expert personas
- [x] Multi-agent backend
- [x] LLM integration
- [x] REST API endpoints
- [x] Parallel agent execution
- [x] Feedback synthesis
- [x] WebSocket support
- [x] Auto agent selection

### Next Up 🚧
- [ ] Connect frontend to backend API
- [ ] Real-time streaming responses
- [ ] Session persistence (database)
- [ ] User authentication
- [ ] Results dashboard
- [ ] PDF report generation
- [ ] Session history
- [ ] Payment integration

## Getting Help

Check these resources:
- API Docs: http://localhost:8000/api/v1/docs
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- OpenAI: https://platform.openai.com/docs
- Anthropic: https://docs.anthropic.com/

## What Makes This Special

🎯 **Multi-Perspective Analysis**: Get feedback from experts across different industries and geographies

🤖 **AI-Powered Insights**: Each agent uses advanced LLMs with carefully crafted prompts

🌍 **Global Coverage**: 14 major business hubs represented

🔄 **Iterative Refinement**: Not just one-off analysis - evolve your idea through multiple rounds

📊 **Synthesis Intelligence**: Automatically identifies consensus and divergent opinions

⚡ **Scalable Architecture**: Built to handle multiple concurrent sessions

## Start Building!

You have everything you need to:
1. ✅ Test the current implementation
2. ✅ Understand the architecture
3. ✅ Connect frontend to backend
4. ✅ Add new features
5. ✅ Deploy to production

**Have fun building Nexus! 🚀**

