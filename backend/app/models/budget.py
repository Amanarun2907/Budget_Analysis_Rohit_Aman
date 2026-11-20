from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class GovernmentLevel(str, enum.Enum):
    UNION = "union"
    STATE = "state"
    UT = "ut"

class DocumentType(str, enum.Enum):
    BUDGET_SPEECH = "budget_speech"
    ANNUAL_FINANCIAL_STATEMENT = "annual_financial_statement"
    EXPENDITURE_BUDGET = "expenditure_budget"
    RECEIPT_BUDGET = "receipt_budget"
    DEMAND_FOR_GRANTS = "demand_for_grants"
    FISCAL_POLICY = "fiscal_policy"
    ECONOMIC_SURVEY = "economic_survey"
    SUPPLEMENTARY_BUDGET = "supplementary_budget"
    OTHER = "other"

class ProcessingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    ANALYZING = "analyzing"
    VISUALIZING = "visualizing"
    COMPLETED = "completed"
    FAILED = "failed"

class EstimateType(str, enum.Enum):
    BUDGET_ESTIMATE = "BE"
    REVISED_ESTIMATE = "RE"
    ACTUAL = "ACTUAL"

class BudgetDocument(Base):
    __tablename__ = "budget_documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workspace_id = Column(String, ForeignKey("budget_workspaces.id"), nullable=False)
    filename = Column(String, nullable=False)
    stored_filename = Column(String)          # alias for filename; kept for compatibility
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)               # bytes
    file_size_bytes = Column(Integer)         # alias; kept for compatibility
    file_type = Column(String)                # pdf, docx, xlsx, etc.
    document_type = Column(String, default=DocumentType.OTHER.value)
    page_count = Column(Integer)
    processing_status = Column(String, default=ProcessingStatus.UPLOADED.value)
    processing_progress = Column(Float, default=0.0)
    processing_error = Column(Text)
    extracted_text = Column(Text)
    extracted_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("BudgetWorkspace", back_populates="documents")
    financial_entries = relationship("FinancialEntry", back_populates="document", cascade="all, delete-orphan")

class BudgetWorkspace(Base):
    __tablename__ = "budget_workspaces"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    government_level = Column(String, default=GovernmentLevel.UNION.value)
    state_name = Column(String)
    financial_year = Column(String)  # e.g., "2024-25"
    description = Column(Text)
    processing_status = Column(String, default=ProcessingStatus.UPLOADED.value)
    processing_progress = Column(Float, default=0.0)
    analysis_completed = Column(Boolean, default=False)
    analysis_result = Column(JSON)  # Complete analysis JSON
    executive_summary = Column(Text)
    budget_highlights = Column(JSON)
    total_receipts = Column(Float)
    total_expenditure = Column(Float)
    fiscal_deficit = Column(Float)
    revenue_deficit = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    documents = relationship("BudgetDocument", back_populates="workspace", cascade="all, delete-orphan")
    financial_entries = relationship("FinancialEntry", back_populates="workspace", cascade="all, delete-orphan")
    sectors = relationship("SectorAnalysis", back_populates="workspace", cascade="all, delete-orphan")
    schemes = relationship("SchemeAnalysis", back_populates="workspace", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="workspace", cascade="all, delete-orphan")

class FinancialEntry(Base):
    __tablename__ = "financial_entries"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workspace_id = Column(String, ForeignKey("budget_workspaces.id"), nullable=False)
    document_id = Column(String, ForeignKey("budget_documents.id"))
    category = Column(String, nullable=False)  # receipt, expenditure, deficit, etc.
    sub_category = Column(String)  # tax_revenue, non_tax_revenue, revenue_expenditure, etc.
    item_name = Column(String, nullable=False)
    amount = Column(Float)
    unit = Column(String, default="crore")  # crore, lakh, million, billion
    financial_year = Column(String)
    estimate_type = Column(String)  # BE, RE, ACTUAL
    percentage_of_total = Column(Float)
    yoy_change = Column(Float)
    ministry = Column(String)
    department = Column(String)
    sector = Column(String)
    source_page = Column(Integer)
    source_table = Column(String)
    source_document = Column(String)
    confidence_score = Column(Float, default=1.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("BudgetWorkspace", back_populates="financial_entries")
    document = relationship("BudgetDocument", back_populates="financial_entries")

class SectorAnalysis(Base):
    __tablename__ = "sector_analyses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workspace_id = Column(String, ForeignKey("budget_workspaces.id"), nullable=False)
    sector_name = Column(String, nullable=False)
    total_allocation = Column(Float)
    previous_allocation = Column(Float)
    percentage_of_total = Column(Float)
    yoy_change = Column(Float)
    key_schemes = Column(JSON)
    analysis_text = Column(Text)
    highlights = Column(JSON)
    sub_sectors = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("BudgetWorkspace", back_populates="sectors")

class SchemeAnalysis(Base):
    __tablename__ = "scheme_analyses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workspace_id = Column(String, ForeignKey("budget_workspaces.id"), nullable=False)
    scheme_name = Column(String, nullable=False)
    ministry = Column(String)
    department = Column(String)
    sector = Column(String)
    current_allocation = Column(Float)
    previous_allocation = Column(Float)
    revised_allocation = Column(Float)
    yoy_change = Column(Float)
    objective = Column(Text)
    beneficiaries = Column(Text)
    analysis_text = Column(Text)
    is_new = Column(Boolean, default=False)
    is_discontinued = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("BudgetWorkspace", back_populates="schemes")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workspace_id = Column(String, ForeignKey("budget_workspaces.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    sources = Column(JSON)  # page references, document names
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("BudgetWorkspace", back_populates="chat_messages")
