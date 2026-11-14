from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Workspace schemas
class WorkspaceCreate(BaseModel):
    name: str
    government_level: str = "union"
    state_name: Optional[str] = None
    financial_year: Optional[str] = None
    description: Optional[str] = None

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    government_level: str
    state_name: Optional[str] = None
    financial_year: Optional[str] = None
    description: Optional[str] = None
    processing_status: Optional[str] = "uploaded"
    processing_progress: Optional[float] = 0.0
    analysis_completed: Optional[bool] = False
    total_receipts: Optional[float] = None
    total_expenditure: Optional[float] = None
    fiscal_deficit: Optional[float] = None
    revenue_deficit: Optional[float] = None
    executive_summary: Optional[str] = None
    budget_highlights: Optional[Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    document_count: int = 0
    
    class Config:
        from_attributes = True

class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
    total: int

# Document schemas
class DocumentResponse(BaseModel):
    id: str
    workspace_id: str
    filename: str
    original_filename: str
    file_type: Optional[str]
    document_type: Optional[str]
    page_count: Optional[int]
    file_size: Optional[int]
    processing_status: str
    processing_progress: float
    processing_error: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Analysis schemas
class AnalysisRequest(BaseModel):
    workspace_id: str

class AnalysisStatusResponse(BaseModel):
    workspace_id: str
    status: str
    progress: float
    current_stage: Optional[str]
    stages: List[Dict[str, Any]]
    error: Optional[str]

class BudgetOverview(BaseModel):
    government_name: str
    financial_year: str
    government_level: str
    state_name: Optional[str]
    total_budget_size: Optional[float]
    total_receipts: Optional[float]
    total_expenditure: Optional[float]
    revenue_receipts: Optional[float]
    capital_receipts: Optional[float]
    revenue_expenditure: Optional[float]
    capital_expenditure: Optional[float]
    fiscal_deficit: Optional[float]
    revenue_deficit: Optional[float]
    primary_deficit: Optional[float]
    fiscal_deficit_gdp_ratio: Optional[float]
    executive_summary: Optional[str]
    key_highlights: Optional[List[str]]
    policy_priorities: Optional[List[str]]
    major_announcements: Optional[List[str]]

class ReceiptAnalysis(BaseModel):
    total_receipts: Optional[float]
    revenue_receipts: Optional[float]
    capital_receipts: Optional[float]
    tax_revenue: Optional[Dict[str, Any]]
    non_tax_revenue: Optional[Dict[str, Any]]
    borrowings: Optional[float]
    disinvestment: Optional[float]
    receipt_composition: Optional[List[Dict[str, Any]]]
    yoy_comparison: Optional[List[Dict[str, Any]]]
    analysis_text: Optional[str]
    charts: Optional[List[Dict[str, Any]]]

class ExpenditureAnalysis(BaseModel):
    total_expenditure: Optional[float]
    revenue_expenditure: Optional[float]
    capital_expenditure: Optional[float]
    ministry_wise: Optional[List[Dict[str, Any]]]
    sector_wise: Optional[List[Dict[str, Any]]]
    expenditure_composition: Optional[List[Dict[str, Any]]]
    top_spending_ministries: Optional[List[Dict[str, Any]]]
    analysis_text: Optional[str]
    charts: Optional[List[Dict[str, Any]]]

class FiscalAnalysis(BaseModel):
    fiscal_deficit: Optional[float]
    revenue_deficit: Optional[float]
    primary_deficit: Optional[float]
    fiscal_deficit_gdp_ratio: Optional[float]
    debt_to_gdp: Optional[float]
    interest_payments: Optional[float]
    total_liabilities: Optional[float]
    fiscal_indicators: Optional[List[Dict[str, Any]]]
    historical_trends: Optional[List[Dict[str, Any]]]
    analysis_text: Optional[str]
    charts: Optional[List[Dict[str, Any]]]

class SectorAnalysisResponse(BaseModel):
    sectors: List[Dict[str, Any]]
    total_sectors: int

class SchemeAnalysisResponse(BaseModel):
    schemes: List[Dict[str, Any]]
    total_schemes: int
    new_schemes: List[Dict[str, Any]]
    discontinued_schemes: List[Dict[str, Any]]

class CompleteAnalysisResponse(BaseModel):
    workspace_id: str
    overview: Optional[BudgetOverview]
    receipts: Optional[ReceiptAnalysis]
    expenditure: Optional[ExpenditureAnalysis]
    fiscal: Optional[FiscalAnalysis]
    sectors: Optional[SectorAnalysisResponse]
    schemes: Optional[SchemeAnalysisResponse]
    macroeconomic: Optional[Dict[str, Any]]
    quality_assessment: Optional[Dict[str, Any]]

# Chat schemas
class ChatRequest(BaseModel):
    workspace_id: str
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    sources: Optional[List[Dict[str, Any]]]
    suggested_questions: Optional[List[str]]

# Report schemas
class ReportRequest(BaseModel):
    workspace_id: str
    format: str = "pdf"  # pdf, csv, xlsx
    sections: Optional[List[str]] = None  # None = all sections

class ReportResponse(BaseModel):
    report_id: str
    download_url: str
    format: str
    generated_at: datetime

# Visualization schemas
class ChartDataRequest(BaseModel):
    workspace_id: str
    chart_type: str
    data_category: str
    filters: Optional[Dict[str, Any]] = None

class ChartDataResponse(BaseModel):
    chart_type: str
    title: str
    data: List[Dict[str, Any]]
    labels: Optional[List[str]]
    units: Optional[str]
    source: Optional[str]
    financial_year: Optional[str]
