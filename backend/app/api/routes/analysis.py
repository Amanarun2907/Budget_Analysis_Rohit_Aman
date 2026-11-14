from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any, List

from app.db.database import get_db
from app.models.budget import (
    BudgetWorkspace, BudgetDocument, FinancialEntry, 
    SectorAnalysis, SchemeAnalysis, ProcessingStatus
)
from app.schemas.budget import (
    AnalysisRequest, AnalysisStatusResponse, CompleteAnalysisResponse,
    BudgetOverview, ReceiptAnalysis, ExpenditureAnalysis, FiscalAnalysis,
    SectorAnalysisResponse, SchemeAnalysisResponse
)
from app.services.analysis.orchestrator import BudgetAnalysisOrchestrator

router = APIRouter()

@router.post("/start")
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == request.workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if documents exist
    doc_result = await db.execute(
        select(BudgetDocument).where(BudgetDocument.workspace_id == request.workspace_id)
    )
    docs = doc_result.scalars().all()
    if not docs:
        raise HTTPException(status_code=400, detail="No documents uploaded yet. Please upload budget documents first.")
    
    # Set status
    workspace.processing_status = ProcessingStatus.PROCESSING.value
    workspace.processing_progress = 5.0
    await db.commit()
    
    # Run orchestrator in background
    background_tasks.add_task(
        BudgetAnalysisOrchestrator.run_analysis,
        request.workspace_id
    )
    
    return {
        "status": "started",
        "workspace_id": request.workspace_id,
        "message": "Analysis started successfully. Progress can be monitored via /status."
    }

@router.get("/status/{workspace_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    progress = workspace.processing_progress or 0.0
    status = workspace.processing_status or ProcessingStatus.UPLOADED.value
    
    stages = [
        {
            "name": "Document Ingestion & OCR",
            "status": "completed" if progress >= 15 else ("in_progress" if status in ["processing", "extracting"] and progress < 15 else "pending"),
            "progress": min(100.0, max(0.0, progress * (100.0 / 15.0)))
        },
        {
            "name": "Vector Store & Knowledge Base",
            "status": "completed" if progress >= 25 else ("in_progress" if progress >= 15 and progress < 25 else "pending"),
            "progress": min(100.0, max(0.0, (progress - 15.0) * 10.0))
        },
        {
            "name": "Financial Extraction & Validation",
            "status": "completed" if progress >= 45 else ("in_progress" if progress >= 25 and progress < 45 else "pending"),
            "progress": min(100.0, max(0.0, (progress - 25.0) * 5.0))
        },
        {
            "name": "Receipts & Expenditure Analysis",
            "status": "completed" if progress >= 65 else ("in_progress" if progress >= 45 and progress < 65 else "pending"),
            "progress": min(100.0, max(0.0, (progress - 45.0) * 5.0))
        },
        {
            "name": "Fiscal, Sector & Scheme Intelligence",
            "status": "completed" if progress >= 85 else ("in_progress" if progress >= 65 and progress < 85 else "pending"),
            "progress": min(100.0, max(0.0, (progress - 65.0) * 5.0))
        },
        {
            "name": "Macroeconomics & Report Generation",
            "status": "completed" if progress >= 100 or status == "completed" else ("in_progress" if progress >= 85 else "pending"),
            "progress": min(100.0, max(0.0, (progress - 85.0) * (100.0 / 15.0)))
        },
    ]
    
    current_stage = "Ready"
    for stage in stages:
        if stage["status"] == "in_progress":
            current_stage = stage["name"]
            break
    if status == "completed":
        current_stage = "Analysis Completed"
    elif status == "failed":
        current_stage = "Analysis Failed"
    
    return AnalysisStatusResponse(
        workspace_id=workspace_id,
        status=status,
        progress=round(progress, 1),
        current_stage=current_stage,
        stages=stages,
        error=None
    )

@router.get("/results/{workspace_id}")
async def get_analysis_results(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return {
        "workspace_id": workspace_id,
        "name": workspace.name,
        "financial_year": workspace.financial_year,
        "government_level": workspace.government_level,
        "state_name": workspace.state_name,
        "processing_status": workspace.processing_status,
        "processing_progress": workspace.processing_progress,
        "analysis_completed": workspace.analysis_completed,
        "analysis": workspace.analysis_result or {},
        "executive_summary": workspace.executive_summary,
        "highlights": workspace.budget_highlights or [],
        "total_receipts": workspace.total_receipts,
        "total_expenditure": workspace.total_expenditure,
        "fiscal_deficit": workspace.fiscal_deficit,
        "revenue_deficit": workspace.revenue_deficit,
    }

@router.get("/overview/{workspace_id}")
async def get_budget_overview(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    analysis = workspace.analysis_result or {}
    return analysis.get("overview", {})

@router.get("/receipts/{workspace_id}")
async def get_receipts_analysis(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    analysis = workspace.analysis_result or {}
    return analysis.get("receipts", {})

@router.get("/expenditure/{workspace_id}")
async def get_expenditure_analysis(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    analysis = workspace.analysis_result or {}
    return analysis.get("expenditure", {})

@router.get("/fiscal/{workspace_id}")
async def get_fiscal_analysis(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    analysis = workspace.analysis_result or {}
    return analysis.get("fiscal", {})

@router.get("/sectors/{workspace_id}")
async def get_sector_analysis(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    analysis = workspace.analysis_result or {}
    return analysis.get("sectors", {})

@router.get("/schemes/{workspace_id}")
async def get_scheme_analysis(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    analysis = workspace.analysis_result or {}
    return analysis.get("schemes", {})

@router.get("/macro/{workspace_id}")
async def get_macro_analysis(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    analysis = workspace.analysis_result or {}
    return analysis.get("macroeconomic", {})

@router.get("/financial-entries/{workspace_id}")
async def get_financial_entries(
    workspace_id: str,
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(FinancialEntry).where(FinancialEntry.workspace_id == workspace_id)
    if category:
        query = query.where(FinancialEntry.category == category)
    if sub_category:
        query = query.where(FinancialEntry.sub_category == sub_category)
    
    result = await db.execute(query)
    entries = result.scalars().all()
    return [
        {c.name: getattr(e, c.name) for c in e.__table__.columns}
        for e in entries
    ]

