from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Cody Foxy"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    DATABASE_URL: str = "postgresql+asyncpg://cody:cody@localhost:5432/codyfoxy"
    REDIS_URL: str = "redis://localhost:6379"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:3000/auth/github/callback"
    GITHUB_APP_ID: str = ""
    GITHUB_APP_PRIVATE_KEY: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    AI_PROVIDER: str = "openai"
    AI_MODEL: str = "gpt-4-turbo-preview"
    
    SCAN_TIMEOUT: int = 300
    MAX_FILE_SIZE: int = 52428800
    MAX_CONCURRENT_SCANS: int = 5
    MAX_SCAN_QUEUE_SIZE: int = 100
    
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    CORS_ORIGINS: str = "http://localhost:3000,https://codyfoxy.dev"
    
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
