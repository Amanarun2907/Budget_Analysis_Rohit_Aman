import React from 'react';
import { 
  Building2, 
  UploadCloud, 
  Sparkles, 
  PieChart, 
  BarChart3, 
  Layers, 
  TrendingUp, 
  Compass, 
  Award, 
  Globe2, 
  FileText, 
  ShieldCheck, 
  FileSpreadsheet, 
  MessageSquareText, 
  ArrowRight,
  ChevronRight,
  CheckCircle2,
  Landmark,
  FileSearch,
  Cpu
} from 'lucide-react';
import { Workspace } from '../types/budget';

interface LandingHeroProps {
  workspaces: Workspace[];
  onOpenUpload: () => void;
  onSelectWorkspace: (w: Workspace) => void;
  onExploreDemo: () => void;
  isDemoLoading: boolean;
}

export const LandingHero: React.FC<LandingHeroProps> = ({
  workspaces,
  onOpenUpload,
  onSelectWorkspace,
  onExploreDemo,
  isDemoLoading,
}) => {
  return (
    <div className="space-y-16 py-8">
      
      {/* 1. Hero Section */}
      <div className="text-center max-w-4xl mx-auto space-y-6">
        
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold shadow-sm">
          <Sparkles className="h-3.5 w-3.5 text-blue-400" />
          <span>AI-Powered Indian Public Finance Intelligence</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        </div>

        {/* Headline */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-[1.15]">
          Analyze Any Indian Budget with <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
            Multi-Agent Economic AI
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed font-normal">
          Upload any official Central Union or State Government budget document — speeches, receipts, expenditures, and demands for grants. Get instant econometric analysis, interactive charts, and zero-hallucination verified accounting figures.
        </p>

        {/* Primary Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-2">
          <button
            onClick={onOpenUpload}
            className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-sm shadow-xl shadow-blue-600/30 flex items-center justify-center gap-2.5 transition-all transform hover:-translate-y-0.5"
          >
            <UploadCloud className="h-5 w-5" />
            <span>Upload Budget Document</span>
            <ArrowRight className="h-4 w-4" />
          </button>

          <button
            onClick={onExploreDemo}
            disabled={isDemoLoading}
            className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-semibold text-sm flex items-center justify-center gap-2.5 transition-all shadow-md disabled:opacity-50"
          >
            <Sparkles className="h-4 w-4 text-indigo-400" />
            <span>{isDemoLoading ? 'Analyzing Sample Budget...' : 'Explore Union Budget Demo'}</span>
          </button>
        </div>

        {/* Trust Points */}
        <div className="flex flex-wrap items-center justify-center gap-6 pt-4 text-xs text-slate-400">
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>Union &amp; All 36 Indian States/UTs</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>PDF, Scanned OCR, Excel &amp; Word</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>100% Deterministic Math Verification</span>
          </div>
        </div>

      </div>

      {/* 2. Recent Analyzed Budgets (If user has existing workspaces) */}
      {workspaces.length > 0 && (
        <div className="max-w-5xl mx-auto space-y-4 pt-4 border-t border-slate-800/80">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Landmark className="h-4 w-4 text-blue-400" />
                Your Analyzed Budget Workspaces ({workspaces.length})
              </h3>
              <p className="text-xs text-slate-400">
                Click any existing budget below to open its full 7-tab dashboard and interactive charts
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {workspaces.map((w) => (
              <div
                key={w.id}
                onClick={() => onSelectWorkspace(w)}
                className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-800/60 cursor-pointer transition-all group shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      {w.government_level}
                    </span>
                    <span className="text-xs font-semibold text-slate-400">
                      FY {w.financial_year || '2024-25'}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-white group-hover:text-blue-300 transition-colors line-clamp-1">
                    {w.name}
                  </h4>
                  {w.state_name && (
                    <p className="text-xs text-slate-400 mt-0.5">
                      State: {w.state_name}
                    </p>
                  )}
                  {w.total_expenditure ? (
                    <div className="mt-3 flex items-center gap-3 text-xs">
                      <div>
                        <span className="text-slate-500 block text-[10px]">Total Outlay</span>
                        <span className="font-bold text-emerald-400">₹{(w.total_expenditure).toLocaleString('en-IN')} Cr</span>
                      </div>
                      {w.fiscal_deficit ? (
                        <div>
                          <span className="text-slate-500 block text-[10px]">Fiscal Deficit</span>
                          <span className="font-bold text-amber-400">₹{(w.fiscal_deficit).toLocaleString('en-IN')} Cr</span>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                </div>

                <div className="mt-4 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-blue-400 group-hover:text-blue-300">
                  <span>Open Intelligence Dashboard</span>
                  <ChevronRight className="h-4 w-4 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. How It Works Pipeline */}
      <div className="max-w-5xl mx-auto space-y-6 pt-4">
        <div className="text-center space-y-1.5">
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            How The Intelligence Pipeline Works
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            From raw government PDFs to verified econometric synthesis in four automated stages
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800/80 relative">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold text-sm mb-3">
              1
            </div>
            <h4 className="text-sm font-bold text-white">Document Ingestion</h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Upload budget speeches, demands for grants, or financial statements in PDF, Excel, or Scanned formats.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800/80 relative">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-sm mb-3">
              2
            </div>
            <h4 className="text-sm font-bold text-white">OCR &amp; Vector Indexing</h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Extracts table matrices, layout hierarchies, and indexes semantic chunks with source page provenance.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800/80 relative">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center font-bold text-sm mb-3">
              3
            </div>
            <h4 className="text-sm font-bold text-white">8-Agent AI Synthesis</h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Specialized public finance agents dissect revenues, capex outlays, sector shares, schemes, and macro trends.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800/80 relative">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-sm mb-3">
              4
            </div>
            <h4 className="text-sm font-bold text-white">Visual Intelligence</h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Explore 7 interactive dashboards, chat with the citation-backed AI Copilot, or export formal PDF reports.
            </p>
          </div>

        </div>
      </div>

      {/* 4. Platform Core Capabilities Grid */}
      <div className="max-w-5xl mx-auto space-y-6 pt-4">
        <div className="text-center space-y-1.5">
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Comprehensive Analytical Modules
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Engineered to meet all 25 public finance intelligence specifications
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
            <div className="p-2 w-fit rounded-lg bg-blue-500/10 text-blue-400">
              <PieChart className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Executive Overview &amp; KPIs</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Aggregated outlay totals, receipts, gross fiscal deficit, revenue deficit, and 500-word synthesized policy narrative.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
            <div className="p-2 w-fit rounded-lg bg-emerald-500/10 text-emerald-400">
              <BarChart3 className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Receipts &amp; Tax Buoyancy</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Dissection of Direct Taxes (Income, Corporation), Indirect Taxes (GST, Customs, Excise), SGST, and non-tax revenues.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
            <div className="p-2 w-fit rounded-lg bg-indigo-500/10 text-indigo-400">
              <Layers className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Expenditure &amp; Capex Outlays</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Asset creation (Capital Expenditure) vs. operational costs (Revenue Expenditure) with ministry-level rankings.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
            <div className="p-2 w-fit rounded-lg bg-amber-500/10 text-amber-400">
              <TrendingUp className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Fiscal Deficit &amp; FRBM Path</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Gross fiscal deficit (% of GDP/GSDP), primary deficit, multi-year historical trendlines, and debt sustainability.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
            <div className="p-2 w-fit rounded-lg bg-purple-500/10 text-purple-400">
              <Compass className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Sectoral Dossiers</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Detailed sector files for Agriculture, Defence, Roads, Railways, Healthcare, Education, Rural Development, and Jal Shakti.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
            <div className="p-2 w-fit rounded-lg bg-cyan-500/10 text-cyan-400">
              <MessageSquareText className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-white">AI Copilot &amp; Reports</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              RAG-grounded natural language Q&amp;A citing exact document pages, plus one-click PDF, Excel, and CSV report export.
            </p>
          </div>

        </div>
      </div>

      {/* 5. Bottom Call-To-Action Banner */}
      <div className="max-w-5xl mx-auto p-8 rounded-2xl bg-gradient-to-r from-blue-900/30 via-slate-900 to-indigo-900/30 border border-blue-500/30 text-center space-y-4">
        <h3 className="text-xl sm:text-2xl font-bold text-white">
          Ready to Analyze an Indian Budget?
        </h3>
        <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto">
          Upload any Central or State budget document to generate interactive visualizations, econometric analysis, and conversational AI answers.
        </p>
        <button
          onClick={onOpenUpload}
          className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-600/30 inline-flex items-center gap-2 transition-all"
        >
          <UploadCloud className="h-4 w-4" />
          <span>Upload Document to Start</span>
        </button>
      </div>

    </div>
  );
};
