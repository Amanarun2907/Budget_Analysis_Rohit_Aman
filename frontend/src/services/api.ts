import { Workspace, AnalysisStatus, CompleteAnalysis, ChatMessage } from '../types/budget';

const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const metaEnv = (import.meta as any).env || {};
const envApiUrl = metaEnv.VITE_API_URL || metaEnv.VITE_BACKEND_URL;
export const API_BASE = isLocal
  ? 'http://127.0.0.1:8000/api'
  : (envApiUrl 
      ? (envApiUrl.endsWith('/api') ? envApiUrl : `${envApiUrl.replace(/\/$/, '')}/api`)
      : 'https://budget-analysis-rohit-aman.onrender.com/api');

export const budgetApi = {
  // Health Check
  async checkHealth(): Promise<{ status: string; service: string; ai_engine?: string }> {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(20000) });
    if (!res.ok) throw new Error('Backend unhealthy');
    return res.json();
  },
  // Workspaces
  async listWorkspaces(): Promise<{ workspaces: Workspace[]; total: number }> {
    const res = await fetch(`${API_BASE}/documents/workspaces`);
    if (!res.ok) throw new Error('Failed to fetch workspaces');
    return res.json();
  },

  async createWorkspace(data: {
    name: string;
    government_level?: string;
    state_name?: string;
    financial_year?: string;
    description?: string;
  }): Promise<Workspace> {
    try {
      const res = await fetch(`${API_BASE}/documents/workspaces`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error (${res.status}): Failed to create workspace`);
      }
      return res.json();
    } catch (e: any) {
      if (e.message?.includes('Failed to fetch') || e.message?.includes('NetworkError')) {
        throw new Error('Cannot connect to backend server at http://127.0.0.1:8000. Please ensure uvicorn is running.');
      }
      throw e;
    }
  },

  async deleteWorkspace(workspaceId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/workspaces/${workspaceId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete workspace');
  },

  // Document Upload
  async uploadDocuments(workspaceId: string, files: File[]): Promise<any> {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));

    const res = await fetch(`${API_BASE}/documents/upload/${workspaceId}`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async listDocuments(workspaceId: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/documents/workspace/${workspaceId}/documents`);
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  // Analysis Lifecycle
  async startAnalysis(workspaceId: string): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/analysis/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workspace_id: workspaceId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to start analysis');
    }
    return res.json();
  },

  async seedDemoBudget(): Promise<Workspace> {
    const res = await fetch(`${API_BASE}/analysis/seed-demo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to seed demo budget');
    }
    return res.json();
  },

  async getAnalysisStatus(workspaceId: string): Promise<AnalysisStatus> {
    const res = await fetch(`${API_BASE}/analysis/status/${workspaceId}`);
    if (!res.ok) throw new Error('Failed to fetch analysis status');
    return res.json();
  },

  async getAnalysisResults(workspaceId: string): Promise<CompleteAnalysis> {
    const res = await fetch(`${API_BASE}/analysis/results/${workspaceId}`);
    if (!res.ok) throw new Error('Failed to fetch analysis results');
    return res.json();
  },

  // Interactive Chat
  async askQuestion(
    workspaceId: string,
    message: string,
    context?: string
  ): Promise<{ message: string; sources?: any[]; suggested_questions?: string[] }> {
    const res = await fetch(`${API_BASE}/chat/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workspace_id: workspaceId,
        message,
        context,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Chat query failed');
    }
    return res.json();
  },

  async getChatHistory(workspaceId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${API_BASE}/chat/history/${workspaceId}`);
    if (!res.ok) throw new Error('Failed to fetch chat history');
    return res.json();
  },

  async clearChatHistory(workspaceId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/chat/history/${workspaceId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to clear chat history');
  },

  // Reports
  async generateReport(
    workspaceId: string,
    format: 'pdf' | 'csv' | 'xlsx' | 'json' = 'pdf'
  ): Promise<{ download_url: string; format: string }> {
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workspace_id: workspaceId,
        format,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Report generation failed');
    }
    return res.json();
  },

  // Union Budget Deep Intelligence & Analysis
  async getUnionIntelligenceOverview(): Promise<any> {
    const res = await fetch(`${API_BASE}/union-intelligence/overview`);
    if (!res.ok) throw new Error('Failed to fetch Union Intelligence overview');
    return res.json();
  },

  async runWhatIfSimulation(data: {
    nominal_gdp_growth_pct: number;
    crude_oil_price_usd: number;
    disinvestment_realization_pct: number;
    tax_buoyancy: number;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/union-intelligence/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to run economic simulation');
    return res.json();
  },

  async calculateTaxRegimes(data: {
    gross_annual_income: number;
    sec_80c_investment?: number;
    sec_80d_health?: number;
    hra_exemption?: number;
    other_deductions?: number;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/union-intelligence/calculate-tax`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to calculate tax comparison');
    return res.json();
  },

  async getUPSCInsights(): Promise<any> {
    const res = await fetch(`${API_BASE}/union-intelligence/upsc-insights`);
    if (!res.ok) throw new Error('Failed to fetch UPSC & Constitutional insights');
    return res.json();
  },

  // Observability, Tracing & Performance Evaluation
  async getObservabilityTrace(workspaceId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/observability/trace/${workspaceId}`);
    if (!res.ok) throw new Error('Failed to fetch observability trace');
    return res.json();
  },

  async getObservabilityMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/observability/metrics`);
    if (!res.ok) throw new Error('Failed to fetch system metrics');
    return res.json();
  },

  // Model Context Protocol (MCP) Tools
  async listMCPTools(): Promise<any> {
    const res = await fetch(`${API_BASE}/mcp/tools`);
    if (!res.ok) throw new Error('Failed to list MCP tools');
    return res.json();
  },

  async executeMCPTool(name: string, args: Record<string, any>): Promise<any> {
    const res = await fetch(`${API_BASE}/mcp/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, arguments: args }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'MCP Tool execution failed');
    }
    return res.json();
  },
};

