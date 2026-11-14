from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import os
import uuid
import aiofiles
from datetime import datetime

from app.db.database import get_db
from app.core.config import settings
from app.models.budget import BudgetDocument, BudgetWorkspace, ProcessingStatus
from app.schemas.budget import DocumentResponse, WorkspaceCreate, WorkspaceResponse, WorkspaceListResponse

router = APIRouter()

@router.post("/workspaces", response_model=WorkspaceResponse)
async def create_workspace(workspace: WorkspaceCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_workspace = BudgetWorkspace(
            id=str(uuid.uuid4()),
            name=workspace.name,
            government_level=workspace.government_level,
            state_name=workspace.state_name,
            financial_year=workspace.financial_year,
            description=workspace.description,
            processing_status=ProcessingStatus.UPLOADED.value,
            processing_progress=0.0,
            analysis_completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_workspace)
        await db.commit()
        await db.refresh(db_workspace)
        
        data_dict = {c.name: getattr(db_workspace, c.name) for c in db_workspace.__table__.columns}
        data_dict["document_count"] = 0
        return WorkspaceResponse(**data_dict)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error creating workspace: {str(e)}")

@router.get("/workspaces", response_model=WorkspaceListResponse)
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BudgetWorkspace).order_by(BudgetWorkspace.created_at.desc()))
    workspaces = result.scalars().all()
    workspace_list = []
    for w in workspaces:
        doc_count_result = await db.execute(
            select(func.count(BudgetDocument.id)).where(BudgetDocument.workspace_id == w.id)
        )
        doc_count = doc_count_result.scalar() or 0
        workspace_list.append(WorkspaceResponse(
            **{c.name: getattr(w, c.name) for c in w.__table__.columns},
            document_count=doc_count
        ))
    return WorkspaceListResponse(workspaces=workspace_list, total=len(workspace_list))

@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    doc_count_result = await db.execute(
        select(func.count(BudgetDocument.id)).where(BudgetDocument.workspace_id == workspace_id)
    )
    doc_count = doc_count_result.scalar() or 0
    return WorkspaceResponse(
        **{c.name: getattr(workspace, c.name) for c in workspace.__table__.columns},
        document_count=doc_count
    )

@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    await db.delete(workspace)
    await db.commit()
    return {"detail": "Workspace deleted"}

@router.post("/upload/{workspace_id}", response_model=List[DocumentResponse])
async def upload_documents(
    workspace_id: str,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    # Verify workspace exists
    result = await db.execute(select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    uploaded_docs = []
    workspace_upload_dir = os.path.join(settings.UPLOAD_DIR, workspace_id)
    os.makedirs(workspace_upload_dir, exist_ok=True)
    
    for file in files:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.xlsx', '.xls', '.csv', '.pptx', '.jpg', '.jpeg', '.png', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(workspace_upload_dir, safe_filename)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Create DB record
        doc = BudgetDocument(
            id=file_id,
            workspace_id=workspace_id,
            filename=safe_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            file_type=file_ext.lstrip('.'),
            processing_status=ProcessingStatus.UPLOADED.value,
        )
        db.add(doc)
        uploaded_docs.append(doc)
    
    # Update workspace status
    workspace.processing_status = ProcessingStatus.UPLOADED.value
    await db.commit()
    
    # Refresh all docs
    for doc in uploaded_docs:
        await db.refresh(doc)
    
    return [DocumentResponse(**{c.name: getattr(d, c.name) for c in d.__table__.columns}) for d in uploaded_docs]

@router.get("/workspace/{workspace_id}/documents", response_model=List[DocumentResponse])
async def list_documents(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BudgetDocument).where(BudgetDocument.workspace_id == workspace_id)
    )
    docs = result.scalars().all()
    return [DocumentResponse(**{c.name: getattr(d, c.name) for c in d.__table__.columns}) for d in docs]
