from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Budget Intelligence Platform",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "ai_engine": f"Groq ({settings.LLM_MODEL})",
        "database": "SQLite (aiosqlite)",
        "features": ["document_processing", "multi_agent_analysis", "rag_chat", "report_export"]
    }
