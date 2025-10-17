"""Application configuration management."""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Nexus"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # LLM Provider
    llm_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-opus-20240229"
    
    # LLM Settings
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 1.0
    
    # Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    max_agents_per_session: int = 10
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/nexus.log"
    
    # Agent Configuration
    default_agent_timeout: int = 30
    max_feedback_rounds: int = 5
    enable_agent_memory: bool = True
    
    # WebSocket
    ws_message_queue_size: int = 100
    ws_heartbeat_interval: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

