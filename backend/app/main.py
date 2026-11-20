from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import structlog
import os
import asyncio

from app.core.config import settings
from app.db.database import init_db
from app.api.routes import documents, analysis, chat, reports, visualizations, health

logger = structlog.get_logger()


async def _recover_stuck_analyses():
    """
    On startup: find any workspace stuck in a non-terminal processing state
    (processing, extracting, analyzing, visualizing) and re-trigger analysis.
    This fixes the Render restart problem where the DB survives but the
    background task was killed mid-flight.
    """
    try:
        from app.db.database import async_session
        from app.models.budget import BudgetWorkspace, BudgetDocument, ProcessingStatus
        from sqlalchemy import select
        from app.services.analysis.orchestrator import BudgetAnalysisOrchestrator

        stuck_statuses = {
            ProcessingStatus.PROCESSING.value,
            ProcessingStatus.EXTRACTING.value,
            ProcessingStatus.ANALYZING.value,
            ProcessingStatus.VISUALIZING.value,
        }

        async with async_session() as db:
            result = await db.execute(select(BudgetWorkspace))
            workspaces = result.scalars().all()
            to_restart = [
                w for w in workspaces
                if (w.processing_status in stuck_statuses and not w.analysis_completed)
            ]

        for ws in to_restart:
            logger.info(f"Restarting stuck analysis for workspace {ws.id} ({ws.name})")
            asyncio.create_task(BudgetAnalysisOrchestrator.run_analysis(ws.id))

        if to_restart:
            logger.info(f"Restarted {len(to_restart)} stuck analysis task(s)")
    except Exception as e:
        logger.warning(f"Recovery check failed (non-fatal): {e}")


async def _ensure_demo_exists():
    """
    Always ensure the Union Budget 2024-25 demo workspace exists on startup.
    This means users can always load the demo instantly, even after Render restarts.
    """
    try:
        from app.db.database import async_session
        from app.models.budget import BudgetWorkspace
        from sqlalchemy import select

        async with async_session() as db:
            result = await db.execute(
                select(BudgetWorkspace).where(BudgetWorkspace.name.ilike("%Union Budget 2024-25%"))
            )
            existing = result.scalars().first()

        if not existing:
            logger.info("Seeding Union Budget 2024-25 demo workspace on startup...")
            from app.services.analysis.demo_seed import get_demo_union_budget_payload
            from app.models.budget import BudgetWorkspace, BudgetDocument, ProcessingStatus
            from app.services.analysis.orchestrator import BudgetAnalysisOrchestrator
            import uuid
            from datetime import datetime

            payload = get_demo_union_budget_payload()
            overview = payload["overview"]
            ws_id = str(uuid.uuid4())

            async with async_session() as db:
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
                    created_at=datetime.utcnow(),
                )
                db.add(doc)
                await db.commit()

            async with async_session() as db:
                await BudgetAnalysisOrchestrator._store_financial_entries(db, ws_id, payload)
                await BudgetAnalysisOrchestrator._store_sector_analyses(db, ws_id, payload)
                await BudgetAnalysisOrchestrator._store_scheme_analyses(db, ws_id, payload)

            logger.info(f"Demo workspace seeded with ID: {ws_id}")
        else:
            logger.info(f"Demo workspace already exists: {existing.id}")

    except Exception as e:
        logger.warning(f"Demo seeding failed (non-fatal): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Budget Intelligence Platform v2...")
    await init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

    # Startup tasks: seed demo + recover stuck analyses
    await _ensure_demo_exists()
    await _recover_stuck_analyses()

    yield
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Union and State Budget Analysis Platform for India",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="", tags=["Health"])  # Allows GET /health directly for monitoring services
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(visualizations.router, prefix="/api/visualizations", tags=["Visualizations"])

# Mount frontend production build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )
