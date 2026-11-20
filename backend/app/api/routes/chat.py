from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.db.database import get_db
from app.models.budget import BudgetWorkspace, ChatMessage
from app.schemas.budget import ChatRequest, ChatResponse
from app.services.rag.chat_engine import BudgetChatEngine

router = APIRouter()


def _analysis_payload(workspace: BudgetWorkspace) -> dict:
    """
    Normalise analysis data so the chat engine receives a consistent structure
    regardless of whether it was seeded (raw dict) or produced by the pipeline
    (also a raw dict).
    """
    result = workspace.analysis_result or {}
    # Both paths store the full dict under analysis_result; return as-is.
    return result


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == request.workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if not workspace.analysis_completed and workspace.processing_status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Analysis is not yet complete. Please wait for the pipeline to finish before asking questions.",
        )

    # Persist user message
    user_msg = ChatMessage(
        workspace_id=request.workspace_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)

    # Build analysis data wrapper that the chat engine understands
    analysis_data = {"analysis": _analysis_payload(workspace)}

    chat_engine = BudgetChatEngine()
    response = await chat_engine.answer_question(
        workspace_id=request.workspace_id,
        question=request.message,
        analysis_data=analysis_data,
        context=request.context,
    )

    # Persist assistant message
    assistant_msg = ChatMessage(
        workspace_id=request.workspace_id,
        role="assistant",
        content=response["answer"],
        sources=response.get("sources"),
    )
    db.add(assistant_msg)
    await db.commit()

    return ChatResponse(
        message=response["answer"],
        sources=response.get("sources"),
        suggested_questions=response.get("suggested_questions"),
    )


@router.get("/history/{workspace_id}")
async def get_chat_history(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.workspace_id == workspace_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return [
        {
            "id":         msg.id,
            "role":       msg.role,
            "content":    msg.content,
            "sources":    msg.sources,
            "created_at": msg.created_at.isoformat(),
        }
        for msg in messages
    ]


@router.delete("/history/{workspace_id}")
async def clear_chat_history(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.workspace_id == workspace_id)
    )
    messages = result.scalars().all()
    for msg in messages:
        await db.delete(msg)
    await db.commit()
    return {"detail": "Chat history cleared"}
