# Tunnel AI Backend

FastAPI backend for AI-powered market research platform.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```

## API Endpoints

### Analysis
- `POST /api/analyze` - Analyze a product idea
- `GET /api/analysis/{id}` - Get analysis results

### Sessions
- `GET /api/sessions` - Get all sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{id}` - Get specific session
- `DELETE /api/sessions/{id}` - Delete session

### WebSocket
- `WS /ws/{session_id}` - Real-time updates

### Health
- `GET /` - Root endpoint
- `GET /health` - Health check

## Project Structure

```
backend/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Dependencies
├── config/
│   ├── settings.py           # App settings
│   └── database.py           # Database config
├── models/
│   ├── database.py           # SQLAlchemy models
│   └── schemas.py            # Pydantic schemas
├── routes/
│   ├── analyze.py            # Analysis endpoints
│   ├── sessions.py           # Session management
│   └── websocket.py          # WebSocket endpoints
└── services/
    ├── openai_service.py     # OpenAI integration
    ├── analysis_service.py   # Analysis logic
    └── realtime_service.py   # WebSocket service
```

## Development

The server runs on `http://localhost:8000` by default.

API documentation is available at `http://localhost:8000/docs`.
