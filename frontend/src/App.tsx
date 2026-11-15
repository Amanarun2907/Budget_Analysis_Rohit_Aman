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
  ArrowRight
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
import { UploadModal } from './components/UploadModal';
import { ChatDrawer } from './components/ChatDrawer';
import { ReportExportModal } from './components/ReportExportModal';
import { budgetApi } from './services/api';
import { Workspace, CompleteAnalysis, AnalysisStatus } from './types/budget';

type TabType = 'overview' | 'receipts' | 'expenditure' | 'fiscal' | 'sectors' | 'schemes' | 'macro';

export default function App() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [analysisData, setAnalysisData] = useState<CompleteAnalysis | null>(null);
  const [statusData, setStatusData] = useState<AnalysisStatus | null>(null);

  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // 1. Initial Load of Workspaces
  useEffect(() => {
    loadWorkspaces();
  }, []);

  // 2. Poll status if workspace is processing
  useEffect(() => {
    let interval: any;
    if (currentWorkspace && currentWorkspace.processing_status !== 'completed' && currentWorkspace.processing_status !== 'failed') {
      interval = setInterval(async () => {
        try {
          const status = await budgetApi.getAnalysisStatus(currentWorkspace.id);
          setStatusData(status);
          if (status.status === 'completed') {
            clearInterval(interval);
            loadAnalysis(currentWorkspace.id);
            loadWorkspaces();
          }
        } catch (e) {
          console.error('Status poll error:', e);
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [currentWorkspace]);

  // 3. Load analysis data when current workspace changes
  useEffect(() => {
    if (currentWorkspace && (currentWorkspace.analysis_completed || currentWorkspace.processing_status === 'completed')) {
      loadAnalysis(currentWorkspace.id);
    } else {
      setAnalysisData(null);
    }
  }, [currentWorkspace]);

  const loadWorkspaces = async () => {
    setIsLoading(true);
    try {
      const res = await budgetApi.listWorkspaces();
      setWorkspaces(res.workspaces);
      // Intentionally do NOT auto-select workspaces so user always lands on the overview & upload page first
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

  const handleCreateSampleBudget = async () => {
    setIsLoading(true);
    try {
      // 1. Instantly seed or retrieve pre-verified 100% accurate Union Budget 2024-25 demo
      const ws = await budgetApi.seedDemoBudget();
      await loadWorkspaces();
      setCurrentWorkspace(ws);
      await loadAnalysis(ws.id);
    } catch (err: any) {
      console.warn('Seed demo fallback to live upload pipeline:', err);
      try {
        const ws = await budgetApi.createWorkspace({
          name: 'Union Budget 2024-25 (Interim & Full)',
          government_level: 'union',
          financial_year: '2024-25',
          description: 'Comprehensive Economic Analysis of Union Budget of India 2024-25',
        });
        const sampleBlob = new Blob([
          `GOVERNMENT OF INDIA\nUNION BUDGET 2024-2025\nTotal Receipts: 3207200 Crore\nTotal Expenditure: 4820512 Crore\nCapital Expenditure: 1111111 Crore\nGross Fiscal Deficit: 1613312 Crore`
        ], { type: 'text/plain' });
        const sampleFile = new File([sampleBlob], 'Union_Budget_2024_25_Summary.txt', { type: 'text/plain' });
        await budgetApi.uploadDocuments(ws.id, [sampleFile]);
        await budgetApi.startAnalysis(ws.id);
        await loadWorkspaces();
        setCurrentWorkspace(ws);
      } catch (innerErr: any) {
        alert(`Error initializing sample budget: ${innerErr.message}`);
      }
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
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      
      {/* Top Navbar */}
      <Navbar
        workspaces={workspaces}
        currentWorkspace={currentWorkspace}
        onSelectWorkspace={(w) => setCurrentWorkspace(w)}
        onOpenUpload={() => setIsUploadOpen(true)}
        onOpenExport={() => setIsExportOpen(true)}
        onToggleChat={() => setIsChatOpen(!isChatOpen)}
        isChatOpen={isChatOpen}
        onGoHome={() => setCurrentWorkspace(null)}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Workspace In-Progress / Processing Banner */}
        {currentWorkspace && currentWorkspace.processing_status !== 'completed' && currentWorkspace.processing_status !== 'failed' && (
          <div className="mb-6 p-5 rounded-2xl bg-slate-900 border border-blue-500/30 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2.5">
                <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
                <div>
                  <h3 className="text-sm font-bold text-white">
                    Multi-Agent Economic Pipeline In Progress
                  </h3>
                  <p className="text-xs text-slate-400">
                    Stage: {statusData?.current_stage || 'Extracting tables & numerical data'}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-sm font-extrabold text-blue-400 font-mono">
                  {statusData ? statusData.progress.toFixed(0) : (currentWorkspace.processing_progress || 0)}%
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full transition-all duration-500 rounded-full"
                style={{ width: `${statusData ? statusData.progress : (currentWorkspace.processing_progress || 5)}%` }}
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
          </div>
        )}

        {/* Dedicated Landing Page & Platform Overview (Shown when no specific budget is selected) */}
        {!currentWorkspace && (
          <LandingHero
            workspaces={workspaces}
            onOpenUpload={() => setIsUploadOpen(true)}
            onSelectWorkspace={(w) => setCurrentWorkspace(w)}
            onExploreDemo={handleCreateSampleBudget}
            isDemoLoading={isLoading}
          />
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
                          ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
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
            {analysisData ? (
              <div>
                {activeTab === 'overview' && <OverviewTab data={analysisData} />}
                {activeTab === 'receipts' && <ReceiptsTab data={analysisData} />}
                {activeTab === 'expenditure' && <ExpenditureTab data={analysisData} />}
                {activeTab === 'fiscal' && <FiscalTab data={analysisData} />}
                {activeTab === 'sectors' && <SectorsTab data={analysisData} />}
                {activeTab === 'schemes' && <SchemesTab data={analysisData} />}
                {activeTab === 'macro' && <MacroTab data={analysisData} />}
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 bg-slate-900/50 rounded-2xl border border-slate-800">
                <Loader2 className="h-6 w-6 animate-spin text-blue-400 mx-auto mb-2" />
                <p className="text-sm">Synthesizing budget analysis...</p>
              </div>
            )}

          </div>
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

