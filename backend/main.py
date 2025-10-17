from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import analyze, sessions, websocket, voice_consult
from config.settings import settings

# Create FastAPI app
app = FastAPI(
    title="Tunnel AI Backend",
    description="AI-powered market research platform with voice consultations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(voice_consult.router, prefix="/api", tags=["Voice Consultation"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tunnel AI Backend is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Tunnel AI Backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
