import React, { useState } from 'react';
import { 
  X, 
  FileDown, 
  FileText, 
  FileSpreadsheet, 
  FileCode, 
  Check, 
  Loader2,
  CheckCircle2
} from 'lucide-react';
import { budgetApi, API_BASE } from '../services/api';

interface ReportExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  workspaceId: string | null;
  budgetName?: string;
}

export const ReportExportModal: React.FC<ReportExportModalProps> = ({
  isOpen,
  onClose,
  workspaceId,
  budgetName,
}) => {
  const [format, setFormat] = useState<'pdf' | 'csv' | 'xlsx' | 'json'>('pdf');
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  if (!isOpen || !workspaceId) return null;

  const handleGenerate = async () => {
    setIsGenerating(true);
    setDownloadUrl(null);
    try {
      const res = await budgetApi.generateReport(workspaceId, format);
      // Build full URL for download (backend serves the file)
      const baseUrl = API_BASE.replace('/api', '');
      setDownloadUrl(res.download_url.startsWith('http') ? res.download_url : `${baseUrl}${res.download_url}`);
    } catch (e: any) {
      alert(`Export error: ${e.message || 'Failed to generate report'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-5">
        
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <FileDown className="h-5 w-5 text-blue-400" />
              Export Budget Report
            </h3>
            <p className="text-xs text-slate-400 mt-0.5 truncate max-w-[280px]">
              {budgetName || 'Intelligence Report'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Format Selectors */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-300">
            Select Report Format
          </label>
          <div className="grid grid-cols-2 gap-2.5">
            
            <button
              type="button"
              onClick={() => { setFormat('pdf'); setDownloadUrl(null); }}
              className={`p-3 rounded-xl border text-left flex items-center gap-3 transition-all ${
                format === 'pdf'
                  ? 'border-red-500 bg-red-500/10 text-white ring-1 ring-red-500'
                  : 'border-slate-800 bg-slate-800/50 text-slate-400 hover:border-slate-700'
              }`}
            >
              <FileText className="h-5 w-5 text-red-400" />
              <div>
                <div className="text-xs font-bold text-white">PDF Dossier</div>
                <div className="text-[10px] text-slate-400">Formal Report</div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => { setFormat('csv'); setDownloadUrl(null); }}
              className={`p-3 rounded-xl border text-left flex items-center gap-3 transition-all ${
                format === 'csv'
                  ? 'border-emerald-500 bg-emerald-500/10 text-white ring-1 ring-emerald-500'
                  : 'border-slate-800 bg-slate-800/50 text-slate-400 hover:border-slate-700'
              }`}
            >
              <FileSpreadsheet className="h-5 w-5 text-emerald-400" />
              <div>
                <div className="text-xs font-bold text-white">CSV Datasets</div>
                <div className="text-[10px] text-slate-400">Excel Compatible</div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => { setFormat('xlsx'); setDownloadUrl(null); }}
              className={`p-3 rounded-xl border text-left flex items-center gap-3 transition-all ${
                format === 'xlsx'
                  ? 'border-green-500 bg-green-500/10 text-white ring-1 ring-green-500'
                  : 'border-slate-800 bg-slate-800/50 text-slate-400 hover:border-slate-700'
              }`}
            >
              <FileSpreadsheet className="h-5 w-5 text-green-400" />
              <div>
                <div className="text-xs font-bold text-white">Excel Workbook</div>
                <div className="text-[10px] text-slate-400">Multi-Sheet Data</div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => { setFormat('json'); setDownloadUrl(null); }}
              className={`p-3 rounded-xl border text-left flex items-center gap-3 transition-all ${
                format === 'json'
                  ? 'border-amber-500 bg-amber-500/10 text-white ring-1 ring-amber-500'
                  : 'border-slate-800 bg-slate-800/50 text-slate-400 hover:border-slate-700'
              }`}
            >
              <FileCode className="h-5 w-5 text-amber-400" />
              <div>
                <div className="text-xs font-bold text-white">JSON API Data</div>
                <div className="text-[10px] text-slate-400">Developers & Models</div>
              </div>
            </button>

          </div>
        </div>

        {/* Action Button */}
        <div className="pt-2">
          {downloadUrl ? (
            <a
              href={downloadUrl}
              download
              target="_blank"
              rel="noreferrer"
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30 transition-all"
            >
              <CheckCircle2 className="h-4 w-4" />
              Download {format.toUpperCase()} Now
            </a>
          ) : (
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-lg shadow-blue-600/30 transition-all"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generating Comprehensive Report...
                </>
              ) : (
                <>
                  <FileDown className="h-4 w-4" />
                  Generate {format.toUpperCase()} Report
                </>
              )}
            </button>
          )}
        </div>

      </div>
    </div>
  );
};

