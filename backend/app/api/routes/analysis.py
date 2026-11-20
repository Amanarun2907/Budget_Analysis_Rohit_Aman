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
from app.services.analysis.demo_seed import get_demo_union_budget_payload
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/seed-demo")
async def seed_demo_workspace(db: AsyncSession = Depends(get_db)):
    """Instantly seed a 100% verified, comprehensive Union Budget 2024-25 analysis demo without waiting."""
    try:
        # Check if already seeded
        result = await db.execute(
            select(BudgetWorkspace).where(BudgetWorkspace.name.ilike("%Union Budget 2024-25%"))
        )
        existing = result.scalars().first()
        payload = get_demo_union_budget_payload()
        overview = payload["overview"]

        if existing:
            workspace = existing
            workspace.analysis_result = payload
            workspace.executive_summary = overview.get("executive_summary")
            workspace.budget_highlights = overview.get("key_highlights")
            workspace.total_receipts = overview.get("total_receipts")
            workspace.total_expenditure = overview.get("total_expenditure")
            workspace.fiscal_deficit = overview.get("fiscal_deficit")
            workspace.revenue_deficit = overview.get("revenue_deficit")
            workspace.processing_status = ProcessingStatus.COMPLETED.value
            workspace.processing_progress = 100.0
            workspace.analysis_completed = True
            workspace.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(workspace)
        else:
            ws_id = str(uuid.uuid4())
            workspace = BudgetWorkspace(
                id=ws_id,
                name="Union Budget 2024-25 (Interim & Full)",
                government_level="union",
                state_name=None,
                financial_year="2024-25",
                description="Comprehensive Economic Analysis of Union Budget of India 2024-25",
                processing_status=ProcessingStatus.COMPLETED.value,
                processing_progress=100.0,
                analysis_completed=True,
                total_receipts=overview.get("total_receipts"),
                total_expenditure=overview.get("total_expenditure"),
                fiscal_deficit=overview.get("fiscal_deficit"),
                revenue_deficit=overview.get("revenue_deficit"),
                executive_summary=overview.get("executive_summary"),
                budget_highlights=overview.get("key_highlights"),
                analysis_result=payload,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(workspace)
            await db.commit()
            await db.refresh(workspace)
            
            # Add demo document record
            doc = BudgetDocument(
                id=str(uuid.uuid4()),
                workspace_id=workspace.id,
                original_filename="Union_Budget_2024_25_Official_Summary.pdf",
                stored_filename="Union_Budget_2024_25_Official_Summary.pdf",
                filename="Union_Budget_2024_25_Official_Summary.pdf",
                file_path="uploads/demo/Union_Budget_2024_25_Official_Summary.pdf",
                file_type="pdf",
                file_size=1048576,
                file_size_bytes=1048576,
                page_count=45,
                processing_status=ProcessingStatus.COMPLETED.value,
                processing_progress=100.0,
                document_type="budget_summary",
                extracted_text=overview.get("executive_summary", ""),
                created_at=datetime.utcnow(),
            )
            db.add(doc)
            await db.commit()

        # Seed relational tables for SQL querying
        await BudgetAnalysisOrchestrator._store_financial_entries(db, workspace.id, payload)
        await BudgetAnalysisOrchestrator._store_sector_analyses(db, workspace.id, payload)
        await BudgetAnalysisOrchestrator._store_scheme_analyses(db, workspace.id, payload)

        return {
            "id": workspace.id,
            "name": workspace.name,
            "government_level": workspace.government_level,
            "state_name": workspace.state_name,
            "financial_year": workspace.financial_year,
            "description": workspace.description,
            "processing_status": workspace.processing_status,
            "processing_progress": workspace.processing_progress,
            "analysis_completed": workspace.analysis_completed,
            "total_receipts": workspace.total_receipts,
            "total_expenditure": workspace.total_expenditure,
            "fiscal_deficit": workspace.fiscal_deficit,
            "revenue_deficit": workspace.revenue_deficit,
            "document_count": 1,
            "created_at": workspace.created_at.isoformat(),
            "updated_at": workspace.updated_at.isoformat(),
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to seed demo: {str(e)}")

@router.post("/start")
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Start budget analysis pipeline.
    - Validates workspace and documents exist
    - Resets status so frontend shows progress immediately
    - Fires analysis in background (non-blocking response)
    """
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
        raise HTTPException(status_code=400, detail="No documents uploaded yet.")

    # Validate uploaded file paths actually exist on disk
    missing_files = [d for d in docs if not __import__('os').path.exists(d.file_path)]
    if missing_files:
        raise HTTPException(
            status_code=422,
            detail=(
                f"{len(missing_files)} uploaded file(s) are missing from disk "
                f"(Render ephemeral disk was likely reset). "
                f"Please delete this workspace and re-upload the files."
            )
        )

    # Reset/init status so frontend sees live progress from 5%
    workspace.processing_status = ProcessingStatus.PROCESSING.value
    workspace.processing_progress = 5.0
    workspace.analysis_completed = False
    await db.commit()

    # Fire analysis as a persistent asyncio Task (not just BackgroundTask)
    # asyncio.create_task survives within the same process — more reliable than
    # FastAPI BackgroundTasks when the response returns before the task finishes.
    import asyncio
    asyncio.create_task(BudgetAnalysisOrchestrator.run_analysis(request.workspace_id))

    return {
        "status": "started",
        "workspace_id": request.workspace_id,
        "message": "Analysis pipeline started. Monitor progress at /api/analysis/status/{workspace_id}."
    }


@router.post("/retry/{workspace_id}")
async def retry_analysis(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retry a failed or stuck analysis.
    Safe to call multiple times — idempotent if already completed.
    """
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if workspace.analysis_completed and workspace.processing_status == ProcessingStatus.COMPLETED.value:
        return {"status": "already_completed", "workspace_id": workspace_id}

    doc_result = await db.execute(
        select(BudgetDocument).where(BudgetDocument.workspace_id == workspace_id)
    )
    docs = doc_result.scalars().all()
    if not docs:
        raise HTTPException(status_code=400, detail="No documents. Please re-upload.")

    missing = [d for d in docs if not __import__('os').path.exists(d.file_path)]
    if missing:
        raise HTTPException(
            status_code=422,
            detail="Uploaded files are missing from disk (Render reset). Delete workspace and re-upload."
        )

    workspace.processing_status = ProcessingStatus.PROCESSING.value
    workspace.processing_progress = 5.0
    workspace.analysis_completed = False
    await db.commit()

    import asyncio
    asyncio.create_task(BudgetAnalysisOrchestrator.run_analysis(workspace_id))

    return {"status": "retrying", "workspace_id": workspace_id}

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

