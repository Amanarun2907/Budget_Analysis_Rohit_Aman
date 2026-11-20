from pydantic_settings import BaseSettings
from typing import Optional
import os

# ─── Persistent paths for Render ────────────────────────────────────────────
# Render free tier has an ephemeral filesystem, but /tmp persists across
# requests within the same process lifetime. We also check for a custom
# PERSIST_DIR env-var that users can set to a Render Disk mount point.
_PERSIST_DIR = os.environ.get("PERSIST_DIR", "")
_DEFAULT_DB_DIR = _PERSIST_DIR if _PERSIST_DIR else "."

class Settings(BaseSettings):
    APP_NAME: str = "Budget Intelligence Platform"
    APP_VERSION: str = "2.0.0"
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GROQ_API_KEY: str = ""
    # Use PERSIST_DIR/budget_intelligence.db if set (Render Disk), else local
    DATABASE_URL: str = f"sqlite+aiosqlite:///{_DEFAULT_DB_DIR}/budget_intelligence.db"
    DATABASE_URL_SYNC: str = f"sqlite:///{_DEFAULT_DB_DIR}/budget_intelligence.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    MAX_UPLOAD_SIZE_MB: int = 500
    UPLOAD_DIR: str = os.path.join(_DEFAULT_DB_DIR, "uploads") if _PERSIST_DIR else "./uploads"
    REPORTS_DIR: str = os.path.join(_DEFAULT_DB_DIR, "reports") if _PERSIST_DIR else "./reports"
    CHROMA_PERSIST_DIR: str = os.path.join(_DEFAULT_DB_DIR, "chroma_db") if _PERSIST_DIR else "./chroma_db"

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Models verified working on this Groq account
    LLM_MODEL: str = "openai/gpt-oss-20b"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 8000
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Analysis tuning
    ANALYSIS_TIMEOUT_SECONDS: int = 180   # max wall-time for full analysis
    AGENT_TIMEOUT_SECONDS: int = 50       # per-agent timeout

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

