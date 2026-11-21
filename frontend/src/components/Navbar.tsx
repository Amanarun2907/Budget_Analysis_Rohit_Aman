import React from 'react';
import { 
  Building2, 
  UploadCloud, 
  FileDown, 
  MessageSquareText, 
  Layers, 
  CheckCircle2, 
  AlertCircle, 
  Loader2,
  ChevronDown,
  Sparkles
} from 'lucide-react';
import { Workspace } from '../types/budget';

interface NavbarProps {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  onSelectWorkspace: (w: Workspace | null) => void;
  onOpenUpload: () => void;
  onOpenExport: () => void;
  onToggleChat: () => void;
  isChatOpen: boolean;
  onGoHome: () => void;
  onOpenUnionIntelligence?: () => void;
  onOpenObservability?: () => void;
  activeViewMode?: 'workspace' | 'union_deep' | 'observability';
}

export const Navbar: React.FC<NavbarProps> = ({
  workspaces,
  currentWorkspace,
  onSelectWorkspace,
  onOpenUpload,
  onOpenExport,
  onToggleChat,
  isChatOpen,
  onGoHome,
  onOpenUnionIntelligence,
  onOpenObservability,
  activeViewMode = 'workspace',
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-900/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Brand - Clickable to return to Home/Landing Page */}
        <div 
          onClick={onGoHome}
          className="flex items-center gap-3 cursor-pointer group select-none transition-transform active:scale-95"
          title="Return to Home & Overview"
        >
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 p-0.5 shadow-lg shadow-blue-500/20 flex items-center justify-center group-hover:shadow-blue-500/40 transition-shadow">
            <div className="h-full w-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Building2 className="h-5 w-5 text-blue-400 group-hover:text-blue-300 transition-colors" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base sm:text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent group-hover:text-blue-200 transition-colors">
                Budget Intelligence
              </span>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                AI Platform
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Union & Indian State Budget Analysis Engine
            </p>
          </div>
        </div>

        {/* Workspace Switcher */}
        <div className="flex items-center gap-3">
          {workspaces.length > 0 && (
            <div className="relative group">
              <select
                className="appearance-none bg-slate-800 border border-slate-700 text-slate-200 text-xs sm:text-sm rounded-lg pl-3 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer max-w-[200px] sm:max-w-[280px] truncate"
                value={currentWorkspace?.id || ''}
                onChange={(e) => {
                  if (!e.target.value) {
                    onSelectWorkspace(null);
                  } else {
                    const w = workspaces.find((x) => x.id === e.target.value);
                    if (w) onSelectWorkspace(w);
                  }
                }}
              >
                <option value="" className="bg-slate-900 text-blue-400 font-semibold">
                  🏠 Home / Platform Overview
                </option>
                {workspaces.map((w) => (
                  <option key={w.id} value={w.id} className="bg-slate-900 text-slate-200">
                    {w.name} {w.financial_year ? `(${w.financial_year})` : ''}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2.5 top-2.5 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
            </div>
          )}

          {currentWorkspace && (
            <button
              onClick={onGoHome}
              className="hidden lg:flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors border border-slate-800"
            >
              <span>← Home</span>
            </button>
          )}

          {currentWorkspace && (
            <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border border-slate-700 bg-slate-800/80">
              {currentWorkspace.processing_status === 'completed' ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  <span className="text-emerald-300">Analyzed</span>
                </>
              ) : currentWorkspace.processing_status === 'failed' ? (
                <>
                  <AlertCircle className="h-3.5 w-3.5 text-red-400" />
                  <span className="text-red-300">Failed</span>
                </>
              ) : (
                <>
                  <Loader2 className="h-3.5 w-3.5 text-blue-400 animate-spin" />
                  <span className="text-blue-300 capitalize">{currentWorkspace.processing_status}</span>
                </>
              )}
            </div>
          )}
        </div>

        {/* Primary Feature Sections: Union Intelligence & Observability */}
        <div className="hidden lg:flex items-center gap-2">
          <button
            onClick={onOpenUnionIntelligence}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeViewMode === 'union_deep'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 ring-1 ring-blue-400'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
            }`}
          >
            <span>🏛️ Union Intelligence</span>
          </button>

          <button
            onClick={onOpenObservability}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeViewMode === 'observability'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30 ring-1 ring-indigo-400'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
            }`}
          >
            <span>⚡ Observability &amp; Tracing</span>
          </button>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenUpload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition-all"
          >
            <UploadCloud className="h-4 w-4" />
            <span className="hidden sm:inline">Upload Budget</span>
          </button>

          {currentWorkspace?.analysis_completed && (
            <button
              onClick={onOpenExport}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all"
              title="Download Comprehensive Report"
            >
              <FileDown className="h-4 w-4 text-slate-300" />
              <span className="hidden sm:inline">Export</span>
            </button>
          )}

          <button
            onClick={onToggleChat}
            className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
              isChatOpen
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
            }`}
          >
            <Sparkles className="h-4 w-4 text-indigo-400" />
            <span className="hidden sm:inline">AI Copilot</span>
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
          </button>
        </div>

      </div>
    </header>
  );
};

