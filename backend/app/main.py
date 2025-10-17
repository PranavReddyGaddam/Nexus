"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1 import research, agents, personas, websocket, analyze


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {settings.app_name} API...")
    print(f"📍 Environment: {settings.app_env}")
    print(f"🤖 LLM Provider: {settings.llm_provider}")
    
    # Initialize services here (database connections, redis, etc.)
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="Multi-Agent Market Research System",
    version="1.0.0",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(
    research.router,
    prefix=f"{settings.api_v1_prefix}/research",
    tags=["research"],
)
app.include_router(
    agents.router,
    prefix=f"{settings.api_v1_prefix}/agents",
    tags=["agents"],
)
app.include_router(
    personas.router,
    prefix=f"{settings.api_v1_prefix}/personas",
    tags=["personas"],
)
app.include_router(
    websocket.router,
    prefix=f"{settings.api_v1_prefix}/ws",
    tags=["websocket"],
)
app.include_router(
    analyze.router,
    prefix=f"{settings.api_v1_prefix}/research",
    tags=["analysis"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "active",
        "environment": settings.app_env,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

