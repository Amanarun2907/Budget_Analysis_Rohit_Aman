from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from app.db.database import get_db
from app.models.budget import BudgetWorkspace
from app.schemas.budget import ReportRequest
from app.services.report.report_generator import ReportGenerator

router = APIRouter()

@router.post("/generate")
async def generate_report(request: ReportRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == request.workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    if not workspace.analysis_completed and workspace.processing_status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    generator = ReportGenerator()
    report_path = await generator.generate_report(
        workspace_id=request.workspace_id,
        analysis_data=workspace.analysis_result,
        format=request.format,
        sections=request.sections,
        workspace_info={
            "name": workspace.name,
            "government_level": workspace.government_level,
            "state_name": workspace.state_name,
            "financial_year": workspace.financial_year,
        }
    )
    
    return {"download_url": f"/api/reports/download/{os.path.basename(report_path)}", "format": request.format}

@router.get("/download/{filename}")
async def download_report(filename: str):
    from app.core.config import settings
    file_path = os.path.join(settings.REPORTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(file_path, filename=filename)
