# Nexus Backend - Multi-Agent Market Research System

## Architecture Overview

The Nexus backend implements a multi-agent system for simulating market research through persona-based expert agents. Each agent represents an industry expert with specialized knowledge and provides feedback on startup ideas through iterative feedback loops.

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **AI/LLM**: OpenAI GPT-4 / Anthropic Claude
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery with Redis
- **Caching**: Redis
- **WebSockets**: For real-time agent responses
- **Authentication**: JWT tokens

## System Components

### 1. Agent System
- **Agent Engine**: Core logic for simulating expert personas
- **Persona Templates**: Pre-defined expert profiles with domain knowledge
- **Context Management**: Maintains conversation history and research context
- **Response Generation**: LLM-powered responses based on persona characteristics

### 2. Orchestration Layer
- **Multi-Agent Coordinator**: Manages multiple agents in parallel
- **Feedback Loop Manager**: Implements iterative refinement process
- **Consensus Engine**: Synthesizes insights from multiple agents
- **Priority Queue**: Manages agent response ordering

### 3. API Layer
- RESTful endpoints for synchronous operations
- WebSocket connections for real-time streaming responses
- Rate limiting and authentication
- Request validation and error handling

### 4. Data Layer
- Research sessions storage
- Agent interaction history
- User profiles and preferences
- Analytics and metrics

## Key Features

### Multi-Agent Feedback Loop
1. User submits startup idea
2. System selects relevant expert personas based on:
   - Industry vertical
   - Geographic market
   - Technology stack
   - Business model
3. Agents provide initial feedback in parallel
4. Feedback is synthesized and presented to user
5. User can refine idea based on feedback
6. Agents review refinements in subsequent rounds
7. Process continues until convergence or user satisfaction

### Agent Personas
- Each agent has unique characteristics:
  - Domain expertise
  - Geographic knowledge
  - Industry experience
  - Communication style
  - Risk tolerance
  - Innovation appetite

### Consensus Building
- Agents can agree, disagree, or build on each other's insights
- System identifies consensus points and divergent opinions
- Highlights critical concerns and opportunities
- Tracks sentiment across feedback rounds

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── research.py     # Research session endpoints
│   │   │   ├── agents.py       # Agent management endpoints
│   │   │   ├── personas.py     # Persona endpoints
│   │   │   └── websocket.py    # WebSocket handlers
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py   # Base agent class
│   │   │   ├── agent_factory.py # Agent creation and management
│   │   │   ├── persona_loader.py # Load persona definitions
│   │   │   └── response_generator.py # LLM integration
│   │   ├── orchestration/
│   │   │   ├── __init__.py
│   │   │   ├── coordinator.py  # Multi-agent coordination
│   │   │   ├── feedback_loop.py # Feedback iteration logic
│   │   │   ├── consensus.py    # Consensus building
│   │   │   └── synthesizer.py  # Response synthesis
│   │   └── llm/
│   │       ├── __init__.py
│   │       ├── providers.py    # LLM provider abstractions
│   │       ├── prompts.py      # Prompt templates
│   │       └── embeddings.py   # Vector embeddings for context
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── research_session.py
│   │   ├── agent_response.py
│   │   ├── feedback_round.py
│   │   └── persona.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── research.py
│   │   ├── agent.py
│   │   ├── persona.py
│   │   └── feedback.py
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── research_service.py
│   │   ├── agent_service.py
│   │   └── analytics_service.py
│   ├── db/                     # Database utilities
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   └── migrations/
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_orchestration.py
│   └── test_api.py
├── data/
│   ├── personas/               # Persona JSON definitions
│   └── prompts/                # Prompt templates
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- OpenAI API key or Anthropic API key

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start Redis (if not running)
redis-server

# Start the application
uvicorn app.main:app --reload --port 8000
```

### Environment Variables

```
# Application
APP_NAME=Nexus
APP_ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nexus

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Provider
LLM_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## API Endpoints

### Research Sessions

**POST /api/v1/research/sessions**
- Create a new research session
- Request body: startup idea, target market, etc.
- Returns: session_id

**GET /api/v1/research/sessions/{session_id}**
- Get session details and all feedback rounds

**POST /api/v1/research/sessions/{session_id}/rounds**
- Start a new feedback round
- Triggers multi-agent analysis

### Agents

**GET /api/v1/agents**
- List all available agent personas

**GET /api/v1/agents/{agent_id}**
- Get specific agent details

**POST /api/v1/agents/select**
- Select agents for a research session
- Request body: criteria for agent selection

### WebSocket

**WS /api/v1/ws/research/{session_id}**
- Real-time streaming of agent responses
- Supports bidirectional communication

## Multi-Agent Workflow

1. **Session Initialization**
   ```
   User submits idea → System creates session → Selects relevant personas
   ```

2. **Round 1 - Initial Analysis**
   ```
   For each selected agent:
     - Agent analyzes idea with their expertise
     - Generates structured feedback
     - Identifies opportunities and risks
   Synthesize all responses → Present to user
   ```

3. **Round 2+ - Iterative Refinement**
   ```
   User provides refinement/clarification
   → Agents review new information
   → Agents respond to each other's feedback
   → Build consensus or highlight disagreements
   → Present synthesized insights
   ```

4. **Conclusion**
   ```
   Generate comprehensive report
   → Key insights from all agents
   → Consensus recommendations
   → Risk assessment
   → Market opportunity score
   ```

## Agent Interaction Patterns

### Parallel Processing
- All agents analyze input simultaneously
- Reduces latency for initial feedback
- Each agent works independently

### Sequential Dialogue
- Agents can respond to each other
- Builds on previous insights
- Creates dynamic discussion

### Consensus Building
- System identifies agreement areas
- Highlights conflicting opinions
- Synthesizes middle ground

## Performance Considerations

- **Caching**: Persona prompts and common queries cached in Redis
- **Async Processing**: All LLM calls are asynchronous
- **Rate Limiting**: Prevents API abuse and controls costs
- **Streaming**: WebSocket responses stream tokens as generated
- **Batch Processing**: Multiple agent calls batched when possible

## Future Enhancements

1. **Agent Learning**: Agents improve based on feedback quality
2. **Custom Personas**: Users can create custom expert personas
3. **Industry-Specific Models**: Fine-tuned models for specific domains
4. **Market Data Integration**: Real-time market data in agent responses
5. **Visualization**: Interactive charts and graphs in feedback
6. **Collaboration**: Multiple users can collaborate on research sessions
7. **Export Options**: PDF, Markdown, or presentation format exports

## Development Guidelines

- Follow PEP 8 style guide
- Write tests for all core functionality
- Document all API endpoints with OpenAPI
- Use type hints throughout
- Implement proper error handling
- Log all agent interactions for analysis

## License

Proprietary - All rights reserved

