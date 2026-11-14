from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "Budget Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    GROQ_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./budget_intelligence.db"
    DATABASE_URL_SYNC: str = "sqlite:///./budget_intelligence.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    MAX_UPLOAD_SIZE_MB: int = 500
    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./reports"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    LLM_MODEL: str = "qwen/qwen3.8-27b"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 8000
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
