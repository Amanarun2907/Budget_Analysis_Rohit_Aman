# Budget Intelligence – AI-Powered Union and State Budget Analysis Platform

An intelligent, full-stack economic analysis and public finance platform for India. This platform automatically ingests, extracts, reconciles, and analyzes the **Union Budget of India** as well as the **Budgets of all 36 Indian States and Union Territories** across any financial year.

Built with **FastAPI**, **SQLAlchemy**, **ChromaDB / Vector Search**, **Multi-Agent AI (Groq LLaMA 3.3 70B & 8B)**, and a **Next-Gen React + Vite + TypeScript + Tailwind CSS** frontend.

---

## 🌟 Key Capabilities

1. **Multi-Format Document Ingestion & Extraction**:
   - Supports PDF, Scanned PDF, Excel (`.xlsx`, `.xls`), CSV, Word (`.docx`), Images (`.jpg`, `.png`), and plain text.
   - Extracts tables, annexures, fiscal policy statements, Demands for Grants, and budget speeches.
   - Preserves source-level traceability and page numbers.

2. **Union & State Budget Intelligence**:
   - Automatically identifies government level (Union vs. State) and jurisdiction (e.g. Government of India, Uttar Pradesh, Maharashtra, Karnataka, etc.).
   - Tailored accounting frameworks: Direct/Indirect Taxes, Customs, and Devolution for the Union; SGST, State Excise, Stamp Duty, Devolution, and GSDP ratios for States.

3. **Multi-Agent AI Analysis Pipeline**:
   - **Orchestrator Agent**: Manages stages and real-time database state.
   - **Overview Agent**: Extracts total receipts, expenditure, deficits, and synthesizes 500-word executive summary.
   - **Receipts Agent**: Deep-dives into Tax Revenue (GST, Income Tax, Corp Tax) and Non-Tax Revenue.
   - **Expenditure Agent**: Analyzes Revenue vs. Capital Outlay (Infrastructure creation) and Ministry rankings.
   - **Fiscal Deficit Agent**: Analyzes Gross Fiscal Deficit, Revenue Deficit, Primary Deficit, and FRBM glide path.
   - **Sectoral Agent**: Evaluates 15+ sectors (Agriculture, Defence, Health, Education, Roads, Railways, MSME, Energy, Jal Shakti, etc.).
   - **Schemes Agent**: Tracks flagship missions (PM-KISAN, MGNREGA, PMAY, Ayushman Bharat, PLI, Jal Jeevan Mission).
   - **Macroeconomic Agent**: Evaluates GDP growth assumptions, inflation, capex multiplier, and "Who Benefits" impact matrix.
   - **Quality & Audit Agent**: Verifies mathematical consistency and reports data limitations.

4. **Interactive AI Budget Copilot (RAG)**:
   - Slide-out conversational AI grounded directly in the uploaded documents.
   - Semantic vector retrieval using ChromaDB and cosine similarity.
   - Provides exact page references and suggested questions.

5. **Visual Dashboards**:
   - High-performance charts using Recharts: Doughnut/Pie charts for receipt & expenditure mix, vertical/horizontal bar charts for ministry allocations, and multi-year deficit trend lines.

6. **Automated Multi-Format Export**:
   - One-click report generation into PDF Dossiers, Excel Workbooks, CSV datasets, and JSON for researchers and policymakers.

---

## 🏗️ Technical Architecture

```
[ User Browser ]
       ▲
       │ (REST APIs + JSON)
       ▼
[ React + Vite + TypeScript Frontend ] (Port 3000)
       ▲
       │ (/api Proxy)
       ▼
[ FastAPI Backend Engine ] (Port 8000)
 ├── Document Processor (PyMuPDF, Tabula, OCR, docx, openpyxl)
 ├── ChromaDB Vector Store (Semantic Embedding Indexing)
 ├── Multi-Agent Intelligence System (Groq API - LLaMA 3.3 70B)
 ├── Deterministic Validation Engine (Arithmetic & Accounting Checks)
 ├── ReportLab PDF / Excel / CSV Exporter
 └── SQLite / PostgreSQL Database (Persistent Workspaces & Entities)
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Node.js 18+ (Tested on Node.js 23.3)
- Groq API Key (Configured in `backend/.env`)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# (Optional) Create virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify environment configuration
# Copy .env.example if .env does not exist:
copy .env.example .env

# Run FastAPI backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will start at `http://localhost:8000`. You can test the interactive Swagger documentation at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```

The frontend will start at `http://localhost:3000`.

---

## 📂 Project Structure

```
PRJ-4/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── analysis.py        # Analysis lifecycle and status endpoints
│   │   │       ├── chat.py            # AI Copilot RAG chat endpoints
│   │   │       ├── documents.py       # Multi-file upload & workspace manager
│   │   │       ├── health.py          # Service health check
│   │   │       ├── reports.py         # Multi-format report export endpoints
│   │   │       └── visualizations.py  # Chart data generator
│   │   ├── core/
│   │   │   └── config.py              # Pydantic environment settings
│   │   ├── db/
│   │   │   ├── base.py                # DeclarativeBase definition
│   │   │   └── database.py            # Async & Sync database connection pool
│   │   ├── models/
│   │   │   └── budget.py              # Comprehensive SQLAlchemy models
│   │   ├── schemas/
│   │   │   └── budget.py              # Pydantic schemas for requests/responses
│   │   └── services/
│   │       ├── analysis/
│   │       │   ├── budget_agents.py   # Multi-agent AI system (Groq LLM)
│   │       │   └── orchestrator.py    # Pipeline coordinator & DB persister
│   │       ├── document_processing/
│   │       │   └── processor.py       # OCR, layout & table extraction
│   │       ├── rag/
│   │       │   ├── chat_engine.py     # Grounded Q&A chat engine
│   │       │   └── vector_store.py    # ChromaDB & semantic chunk indexer
│   │       └── report/
│   │           └── report_generator.py # PDF/Excel/CSV generator
│   ├── tests/
│   │   └── test_api.py                # Automated unit tests
│   ├── .env                           # Environment variables with Groq API key
│   ├── requirements.txt               # Pinned Python dependencies
│   └── main.py                        # FastAPI entry point
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatDrawer.tsx         # Slide-out AI Budget Copilot
│   │   │   ├── ExpenditureTab.tsx     # Capex vs Revex & Ministry rankings
│   │   │   ├── FiscalTab.tsx          # Deficit indicators & FRBM glide path
│   │   │   ├── MacroTab.tsx           # GDP growth & Demographic impact
│   │   │   ├── Navbar.tsx             # Brand header & workspace selector
│   │   │   ├── OverviewTab.tsx        # KPI cards, Executive summary & charts
│   │   │   ├── ReceiptsTab.tsx        # Tax & Non-tax revenue analysis
│   │   │   ├── ReportExportModal.tsx  # Download PDF/CSV/Excel/JSON
│   │   │   ├── SchemesTab.tsx         # Welfare schemes & mission tracker
│   │   │   ├── SectorsTab.tsx         # Sector-wise allocations & analysis
│   │   │   └── UploadModal.tsx        # Multi-document upload dialog
│   │   ├── services/
│   │   │   └── api.ts                 # Typed API client
│   │   ├── types/
│   │   │   └── budget.ts              # TypeScript interfaces
│   │   ├── App.tsx                    # Main dashboard application
│   │   └── main.tsx                   # React root entry
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── samples/
│   ├── union_budget_2024_25.txt       # Sample official Union Budget document
│   └── uttar_pradesh_state_budget_2024_25.txt # Sample State Budget document
└── README.md                          # Documentation
```

---

## 🧪 Testing with Sample Budgets

Sample documents are included in the `samples/` directory:
- `samples/union_budget_2024_25.txt`: Complete figures for the Union Budget of India 2024-25.
- `samples/uttar_pradesh_state_budget_2024_25.txt`: Complete figures for the Uttar Pradesh State Budget 2024-25.

You can upload either file through the **Upload Budget** button in the dashboard or click **Explore Union Budget 2024-25 Demo** to run an analysis immediately.

---

## 🔒 Security & Guardrails
- **Deterministic Validation**: Financial subtotals and accounting checks are performed deterministically rather than relying on probabilistic LLM math.
- **Source Traceability**: Every extracted figure references its source document and page number.
- **Zero-Hallucination Guardrails**: Prompts explicitly forbid generating unsupported financial values. Missing data points are tagged as `null` or unrecorded.
- **Environment Isolation**: API keys and secrets are loaded strictly from `.env`.

