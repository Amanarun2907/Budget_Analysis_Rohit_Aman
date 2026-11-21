import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  UploadCloud, 
  PieChart, 
  BarChart3, 
  TrendingUp, 
  Award, 
  Compass, 
  Globe2, 
  FileText, 
  Loader2, 
  AlertCircle, 
  Sparkles, 
  RefreshCw,
  Layers,
  ArrowRight,
  Landmark,
  Activity
} from 'lucide-react';
import { Navbar } from './components/Navbar';
import { LandingHero } from './components/LandingHero';
import { OverviewTab } from './components/OverviewTab';
import { ReceiptsTab } from './components/ReceiptsTab';
import { ExpenditureTab } from './components/ExpenditureTab';
import { FiscalTab } from './components/FiscalTab';
import { SectorsTab } from './components/SectorsTab';
import { SchemesTab } from './components/SchemesTab';
import { MacroTab } from './components/MacroTab';
import { UnionBudgetIntelligence } from './components/UnionBudgetIntelligence';
import { ObservabilityTab } from './components/ObservabilityTab';
import { UploadModal } from './components/UploadModal';
import { ChatDrawer } from './components/ChatDrawer';
import { ReportExportModal } from './components/ReportExportModal';
import { budgetApi } from './services/api';
import { Workspace, CompleteAnalysis, AnalysisStatus } from './types/budget';

type TabType = 'overview' | 'receipts' | 'expenditure' | 'fiscal' | 'sectors' | 'schemes' | 'macro' | 'union_deep' | 'observability';

export default function App() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [globalMode, setGlobalMode] = useState<'workspace' | 'union_deep' | 'observability'>('workspace');
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [analysisData, setAnalysisData] = useState<CompleteAnalysis | null>(null);
  const [statusData, setStatusData] = useState<AnalysisStatus | null>(null);

  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isRetrying, setIsRetrying] = useState(false);
  const [workspaceLostError, setWorkspaceLostError] = useState(false);

  // 1. Initial Load of Workspaces
  useEffect(() => {
    loadWorkspaces();
  }, []);

  // 2. Poll status if workspace is processing or uploaded
  useEffect(() => {
    let interval: any;
    setWorkspaceLostError(false);

    if (currentWorkspace && currentWorkspace.processing_status !== 'completed' && currentWorkspace.processing_status !== 'failed') {
      // Auto-trigger analysis if currently in 'uploaded' state
      if (currentWorkspace.processing_status === 'uploaded') {
        budgetApi.startAnalysis(currentWorkspace.id).catch((err) => {
          console.warn('Auto-trigger startAnalysis error:', err);
        });
      }

      interval = setInterval(async () => {
        try {
          const status = await budgetApi.getAnalysisStatus(currentWorkspace.id);
          setStatusData(status);

          // Update currentWorkspace progress in real time so the UI progress bar smoothly updates
          if (status.progress) {
            setCurrentWorkspace((prev) => prev ? {
              ...prev,
              processing_status: status.status as any,
              processing_progress: status.progress,
            } : null);
          }

          if (status.status === 'completed') {
            clearInterval(interval);
            setCurrentWorkspace((prev) => prev ? {
              ...prev,
              processing_status: 'completed',
              processing_progress: 100.0,
              analysis_completed: true,
            } : null);
            await loadAnalysis(currentWorkspace.id);
            await loadWorkspaces();
          } else if (status.status === 'uploaded') {
            // Re-trigger if still sitting in uploaded
            budgetApi.startAnalysis(currentWorkspace.id).catch(() => {});
          } else if (status.status === 'failed') {
            clearInterval(interval);
            setCurrentWorkspace((prev) => prev ? {
              ...prev,
              processing_status: 'failed',
            } : null);
          }
        } catch (e: any) {
          console.error('Status poll error:', e);
          const msg = e.message || '';
          if (msg.includes('404') || msg.includes('not found') || msg.includes('Workspace not found')) {
            clearInterval(interval);
            setWorkspaceLostError(true);
          }
        }
      }, 2500);
    }
    return () => clearInterval(interval);
  }, [currentWorkspace?.id, currentWorkspace?.processing_status]);

  // 3. Load analysis data when current workspace changes or completes
  useEffect(() => {
    if (currentWorkspace && (currentWorkspace.analysis_completed || currentWorkspace.processing_status === 'completed')) {
      loadAnalysis(currentWorkspace.id);
    } else {
      setAnalysisData(null);
    }
  }, [currentWorkspace?.id, currentWorkspace?.processing_status, currentWorkspace?.analysis_completed]);

  const loadWorkspaces = async () => {
    setIsLoading(true);
    try {
      const res = await budgetApi.listWorkspaces();
      setWorkspaces(res.workspaces);
      setCurrentWorkspace((curr) => {
        if (!curr) return null;
        const fresh = res.workspaces.find((w: Workspace) => w.id === curr.id);
        return fresh ? { ...curr, ...fresh } : curr;
      });
    } catch (e) {
      console.error('Failed to load workspaces:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const loadAnalysis = async (workspaceId: string) => {
    try {
      const res = await budgetApi.getAnalysisResults(workspaceId);
      setAnalysisData(res);
    } catch (e) {
      console.error('Failed to load analysis:', e);
    }
  };

  const handleRetryAnalysis = async () => {
    if (!currentWorkspace) return;
    setIsRetrying(true);
    try {
      await budgetApi.startAnalysis(currentWorkspace.id);
      setCurrentWorkspace({
        ...currentWorkspace,
        processing_status: 'processing',
        processing_progress: 5.0,
      });
    } catch (err: any) {
      console.error('Retry analysis error:', err);
      alert('Could not restart analysis: ' + (err.message || 'Server error. Please re-upload.'));
    } finally {
      setIsRetrying(false);
    }
  };

  const handleCreateSampleBudget = async () => {
    setIsLoading(true);
    try {
      // Seed or retrieve pre-verified Union Budget 2024-25 demo data
      const ws = await budgetApi.seedDemoBudget();
      await loadWorkspaces();
      setCurrentWorkspace(ws);
      await loadAnalysis(ws.id);
    } catch (err: any) {
      console.warn('Seed demo failed:', err);
      alert('Could not load the demo budget. Please upload a real budget PDF using the Upload Budget button.');
    } finally {
      setIsLoading(false);
    }
  };

  const navTabs = [
    { id: 'overview', label: 'Executive Overview', icon: PieChart },
    { id: 'receipts', label: 'Receipts & Revenue', icon: BarChart3 },
    { id: 'expenditure', label: 'Expenditure & Outlay', icon: Layers },
    { id: 'fiscal', label: 'Fiscal Health & Deficit', icon: TrendingUp },
    { id: 'sectors', label: 'Sectoral Analysis', icon: Compass },
    { id: 'schemes', label: 'Schemes & Missions', icon: Award },
    { id: 'macro', label: 'Macroeconomics', icon: Globe2 },
    { id: 'union_deep', label: '🏛️ Union Intelligence', icon: Landmark },
    { id: 'observability', label: '⚡ Tracing & Evaluation', icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      
      {/* Top Navbar */}
      <Navbar
        workspaces={workspaces}
        currentWorkspace={currentWorkspace}
        onSelectWorkspace={(w) => {
          setGlobalMode('workspace');
          setCurrentWorkspace(w);
        }}
        onOpenUpload={() => setIsUploadOpen(true)}
        onOpenExport={() => setIsExportOpen(true)}
        onToggleChat={() => setIsChatOpen(!isChatOpen)}
        isChatOpen={isChatOpen}
        onGoHome={() => {
          setGlobalMode('workspace');
          setCurrentWorkspace(null);
        }}
        onOpenUnionIntelligence={() => {
          setGlobalMode('union_deep');
          setActiveTab('union_deep');
        }}
        onOpenObservability={() => {
          setGlobalMode('observability');
          setActiveTab('observability');
        }}
        activeViewMode={globalMode}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Dedicated Standalone Union Intelligence Section */}
        {globalMode === 'union_deep' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-1">
              <button
                onClick={() => setGlobalMode('workspace')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-blue-400 hover:text-blue-300 border border-slate-800 transition-colors shadow-sm"
              >
                <span>← Back to Workspace &amp; Upload</span>
              </button>
            </div>
            <UnionBudgetIntelligence />
          </div>
        )}

        {/* Dedicated Standalone Observability, Tracing & Performance Section */}
        {globalMode === 'observability' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-1">
              <button
                onClick={() => setGlobalMode('workspace')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-indigo-400 hover:text-indigo-300 border border-slate-800 transition-colors shadow-sm"
              >
                <span>← Back to Workspace &amp; Upload</span>
              </button>
            </div>
            <ObservabilityTab workspaceId={currentWorkspace?.id} />
          </div>
        )}

        {/* Normal Workspace Flow */}
        {globalMode === 'workspace' && (
          <>
            {/* Workspace In-Progress / Processing Banner */}
            {currentWorkspace && currentWorkspace.processing_status !== 'completed' && currentWorkspace.processing_status !== 'failed' && (
              <div className="mb-6 p-5 rounded-2xl bg-slate-900 border border-blue-500/30 shadow-xl space-y-4">
                
                {/* If server wiped ephemeral database */}
                {workspaceLostError ? (
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5 text-amber-400 shrink-0" />
                      <span className="text-xs">
                        This budget session expired when the cloud server restarted. Please re-upload your budget or explore the verified demo budget.
                      </span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => handleCreateSampleBudget()}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-colors"
                      >
                        Load Demo Budget
                      </button>
                      <button
                        onClick={() => setIsUploadOpen(true)}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
                      >
                        Re-upload Document
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
                        <div>
                          <h3 className="text-sm font-bold text-white flex items-center gap-2">
                            <span>Multi-Agent Economic Pipeline In Progress</span>
                            {currentWorkspace.processing_status === 'uploaded' && (
                              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono">
                                Initiating AI Agents...
                              </span>
                            )}
                          </h3>
                          <p className="text-xs text-slate-400">
                            Stage: {statusData?.current_stage || (currentWorkspace.processing_status === 'uploaded' ? 'Initiating Extraction Pipeline...' : 'Extracting tables & numerical data')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <button
                          onClick={handleRetryAnalysis}
                          disabled={isRetrying}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                          title="Force restart analysis if stalled"
                        >
                          <RefreshCw className={`h-3 w-3 ${isRetrying ? 'animate-spin' : ''}`} />
                          <span>{isRetrying ? 'Starting...' : 'Restart Analysis'}</span>
                        </button>
                        <span className="text-sm font-extrabold text-blue-400 font-mono">
                          {statusData ? statusData.progress.toFixed(0) : (currentWorkspace.processing_progress || 0)}%
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full transition-all duration-500 rounded-full"
                        style={{ width: `${Math.max(5, statusData ? statusData.progress : (currentWorkspace.processing_progress || 5))}%` }}
                      />
                    </div>

                    {/* Pipeline Stage Pills */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 pt-1">
                      {(statusData?.stages || [
                        { name: 'Document OCR', status: 'completed' },
                        { name: 'Vector Store', status: 'in_progress' },
                        { name: 'Financial Extraction', status: 'pending' },
                        { name: 'Revenue & Outlay', status: 'pending' },
                        { name: 'Deficit & Sectors', status: 'pending' },
                        { name: 'Report Generation', status: 'pending' },
                      ]).map((st: any, i: number) => (
                        <div
                          key={i}
                          className={`px-2.5 py-1.5 rounded-lg text-[10px] font-semibold text-center border truncate ${
                            st.status === 'completed'
                              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                              : st.status === 'in_progress'
                              ? 'bg-blue-500/20 border-blue-500/40 text-blue-300 animate-pulse'
                              : 'bg-slate-800/40 border-slate-800 text-slate-500'
                          }`}
                        >
                          {st.name}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Dedicated Landing Page & Platform Overview (Shown when no specific budget is selected) */}
            {!currentWorkspace && (
              <div className="space-y-6">
                <LandingHero
                  workspaces={workspaces}
                  onOpenUpload={() => setIsUploadOpen(true)}
                  onSelectWorkspace={(w) => setCurrentWorkspace(w)}
                  onExploreDemo={handleCreateSampleBudget}
                  isDemoLoading={isLoading}
                />

                {/* Additional Quick-Action Enterprise Cards on Home */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div 
                    onClick={() => { setGlobalMode('union_deep'); setActiveTab('union_deep'); }}
                    className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-blue-950/40 border border-blue-800/40 hover:border-blue-500/60 transition-all cursor-pointer shadow-lg group"
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2.5 rounded-xl bg-blue-500/20 text-blue-400 group-hover:scale-110 transition-transform">
                        <Landmark className="h-6 w-6" />
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white group-hover:text-blue-300 transition-colors">
                          Union Budget Deep Intelligence Section
                        </h3>
                        <span className="text-[11px] text-blue-400 font-semibold">10-Year Longitudinal Analysis &amp; What-If Simulator</span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Explore Rupee Flows (where rupee comes from/goes to), 10-year BE vs RE vs Actual trends, 
                      subsidies rationalization, 15th Finance Commission devolution, and interactive economic policy simulation.
                    </p>
                    <div className="mt-3 text-xs font-semibold text-blue-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                      <span>Launch Union Intelligence</span>
                      <span>→</span>
                    </div>
                  </div>

                  <div 
                    onClick={() => { setGlobalMode('observability'); setActiveTab('observability'); }}
                    className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-indigo-950/40 border border-indigo-800/40 hover:border-indigo-500/60 transition-all cursor-pointer shadow-lg group"
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400 group-hover:scale-110 transition-transform">
                        <Activity className="h-6 w-6" />
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white group-hover:text-indigo-300 transition-colors">
                          Agent Observability, Provenance &amp; Evaluation
                        </h3>
                        <span className="text-[11px] text-indigo-400 font-semibold">Langfuse-Compatible Tracing &amp; Audit Trail</span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Inspect execution latency waterfalls, per-agent token accounting, inference cost telemetry, 
                      deterministic mathematical reconciliation audits, and run interactive Model Context Protocol (MCP) tools.
                    </p>
                    <div className="mt-3 text-xs font-semibold text-indigo-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                      <span>View Traces &amp; Metrics</span>
                      <span>→</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Workspace Active Analytics Dashboard (Shown after budget selection/upload) */}
            {currentWorkspace && (
              <div className="space-y-6">

                {/* Navigation Breadcrumb / Back button */}
                <div className="flex items-center justify-between pb-1">
                  <button
                    onClick={() => setCurrentWorkspace(null)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-blue-400 hover:text-blue-300 border border-slate-800 transition-colors shadow-sm"
                  >
                    <span>← Back to Platform Overview &amp; Upload</span>
                  </button>
                </div>
                
                {/* Header info badge */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800/80">
                  <div>
                    <div className="flex items-center gap-2">
                      <h1 className="text-lg sm:text-xl font-extrabold text-white">
                        {currentWorkspace.name}
                      </h1>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {currentWorkspace.government_level}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Financial Year: <span className="font-semibold text-slate-200">{currentWorkspace.financial_year || '2024-25'}</span>
                      {currentWorkspace.state_name && ` • State: ${currentWorkspace.state_name}`}
                    </p>
                  </div>

                  {/* Navigation Tabs Bar */}
                  <div className="flex items-center gap-1.5 overflow-x-auto pb-1 max-w-full no-scrollbar">
                    {navTabs.map((tab) => {
                      const Icon = tab.icon;
                      const isActive = activeTab === tab.id;
                      return (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id as TabType)}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                            isActive
                              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 ring-1 ring-blue-400'
                              : 'bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800'
                          }`}
                        >
                          <Icon className="h-3.5 w-3.5" />
                          <span>{tab.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Tab Contents */}
                <div>
                  {activeTab === 'overview' && analysisData && <OverviewTab data={analysisData} />}
                  {activeTab === 'receipts' && analysisData && <ReceiptsTab data={analysisData} />}
                  {activeTab === 'expenditure' && analysisData && <ExpenditureTab data={analysisData} />}
                  {activeTab === 'fiscal' && analysisData && <FiscalTab data={analysisData} />}
                  {activeTab === 'sectors' && analysisData && <SectorsTab data={analysisData} />}
                  {activeTab === 'schemes' && analysisData && <SchemesTab data={analysisData} />}
                  {activeTab === 'macro' && analysisData && <MacroTab data={analysisData} />}
                  {activeTab === 'union_deep' && <UnionBudgetIntelligence />}
                  {activeTab === 'observability' && <ObservabilityTab workspaceId={currentWorkspace.id} />}

                  {!analysisData && activeTab !== 'union_deep' && activeTab !== 'observability' && (
                    <div className="p-12 text-center text-slate-500 bg-slate-900/50 rounded-2xl border border-slate-800">
                      <Loader2 className="h-6 w-6 animate-spin text-blue-400 mx-auto mb-2" />
                      <p className="text-sm">Synthesizing budget analysis...</p>
                    </div>
                  )}
                </div>

              </div>
            )}
          </>
        )}

      </main>

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onWorkspaceCreated={(ws) => {
          loadWorkspaces();
          setCurrentWorkspace(ws);
        }}
      />

      {/* Export Report Modal */}
      <ReportExportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        workspaceId={currentWorkspace?.id || null}
        budgetName={currentWorkspace?.name}
      />

      {/* Slide-out AI Chat Drawer */}
      <ChatDrawer
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        workspaceId={currentWorkspace?.id || null}
        budgetName={currentWorkspace?.name}
      />

    </div>
  );
}

