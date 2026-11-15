export interface Workspace {
  id: string;
  name: string;
  government_level: 'union' | 'state' | 'ut';
  state_name?: string | null;
  financial_year?: string | null;
  description?: string | null;
  processing_status: 'uploaded' | 'processing' | 'extracting' | 'validating' | 'analyzing' | 'visualizing' | 'completed' | 'failed';
  processing_progress: number;
  analysis_completed: boolean;
  total_receipts?: number | null;
  total_expenditure?: number | null;
  fiscal_deficit?: number | null;
  revenue_deficit?: number | null;
  executive_summary?: string | null;
  budget_highlights?: string[] | null;
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  workspace_id: string;
  filename: string;
  original_filename: string;
  file_type?: string;
  document_type?: string;
  page_count?: number;
  file_size?: number;
  processing_status: string;
  processing_progress: number;
  created_at: string;
}

export interface PipelineStage {
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
}

export interface AnalysisStatus {
  workspace_id: string;
  status: string;
  progress: number;
  current_stage?: string;
  stages: PipelineStage[];
  error?: string | null;
}

export interface SectorItem {
  sector_name?: string;
  name?: string;
  total_allocation?: number;
  allocation?: number;
  previous_allocation?: number | null;
  percentage_of_total?: number;
  percentage?: number;
  yoy_change?: number | null;
  key_schemes?: string[];
  key_announcements?: string[];
  analysis?: string;
  highlights?: string[];
  economic_impact?: string;
}

export interface SchemeItem {
  scheme_name?: string;
  name?: string;
  ministry?: string | null;
  department?: string | null;
  sector?: string;
  current_allocation?: number;
  allocation?: number;
  previous_allocation?: number | null;
  yoy_change?: number | null;
  objective?: string;
  beneficiaries?: string;
  analysis?: string;
  is_new?: boolean;
  is_discontinued?: boolean;
}

export interface CompleteAnalysis {
  workspace_id: string;
  name?: string;
  financial_year?: string;
  government_level?: string;
  state_name?: string | null;
  processing_status?: string;
  processing_progress?: number;
  analysis_completed?: boolean;
  executive_summary?: string;
  highlights?: string[];
  total_receipts?: number;
  total_expenditure?: number;
  fiscal_deficit?: number;
  revenue_deficit?: number;
  analysis: {
    overview?: {
      government_name?: string;
      financial_year?: string;
      government_level?: string;
      state_name?: string;
      total_budget_size?: number;
      total_receipts?: number;
      total_expenditure?: number;
      revenue_receipts?: number;
      capital_receipts?: number;
      revenue_expenditure?: number;
      capital_expenditure?: number;
      fiscal_deficit?: number;
      revenue_deficit?: number;
      primary_deficit?: number;
      fiscal_deficit_gdp_ratio?: number;
      executive_summary?: string;
      key_highlights?: string[];
      policy_priorities?: string[];
      major_announcements?: string[];
    };
    receipts?: {
      total_receipts?: number;
      revenue_receipts?: number;
      capital_receipts?: number;
      tax_revenue?: Record<string, any>;
      non_tax_revenue?: Record<string, any>;
      borrowings?: number;
      disinvestment?: number;
      receipt_composition?: Array<{ name: string; value: number; percentage: number }>;
      analysis_text?: string;
      dependency_observation?: string;
    };
    expenditure?: {
      total_expenditure?: number;
      revenue_expenditure?: number;
      capital_expenditure?: number;
      interest_payments?: number;
      subsidies?: number;
      pensions?: number;
      defence_expenditure?: number;
      ministry_wise?: Array<{ name: string; allocation: number; percentage: number; yoy_change?: number }>;
      top_spending_ministries?: Array<{ name: string; allocation: number; percentage: number }>;
      expenditure_composition?: Array<{ name: string; value: number; percentage: number }>;
      capital_outlay_ratio?: number;
      analysis_text?: string;
    };
    fiscal?: {
      fiscal_deficit?: number;
      fiscal_deficit_gdp_ratio?: number;
      revenue_deficit?: number;
      primary_deficit?: number;
      interest_payments?: number;
      debt_to_gdp_ratio?: number;
      fiscal_indicators?: Array<{ name: string; value: any; unit: string; status: string; explanation: string }>;
      historical_trends?: Array<{ year: string; fiscal_deficit: number; revenue_deficit?: number; primary_deficit?: number }>;
      frbm_assessment?: string;
      analysis_text?: string;
    };
    sectors?: {
      sectors?: SectorItem[];
      total_sectors?: number;
      highest_allocation_sector?: string;
      fastest_growing_sector?: string;
      analysis_text?: string;
    };
    schemes?: {
      schemes?: SchemeItem[];
      total_schemes?: number;
      new_schemes?: Array<{ name: string; allocation?: number; objective?: string }>;
      top_funded_schemes?: Array<{ name: string; allocation: number }>;
      analysis_text?: string;
    };
    macroeconomic?: {
      nominal_gdp?: number;
      real_gdp_growth_assumption?: number;
      nominal_gdp_growth_assumption?: number;
      inflation_assumption?: number;
      fiscal_deficit_gdp_ratio?: number;
      tax_to_gdp_ratio?: number;
      capex_to_gdp_ratio?: number;
      growth_impact?: string;
      inflation_impact?: string;
      employment_impact?: string;
      risks?: string[];
      opportunities?: string[];
      who_benefits?: Array<{ group: string; impact: string; explanation: string }>;
      economic_indicators?: Array<{ name: string; value: string; significance: string }>;
      analysis_text?: string;
    };
    quality_assessment?: {
      data_completeness?: number;
      data_quality_score?: number;
      extraction_confidence?: number;
      strengths?: string[];
      limitations?: string[];
      disclaimer?: string;
    };
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    text: string;
    page: string | number;
    source: string;
    relevance?: number;
  }>;
  created_at: string;
}

