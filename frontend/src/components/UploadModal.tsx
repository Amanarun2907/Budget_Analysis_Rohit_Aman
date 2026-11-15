import React, { useState, useRef, useEffect } from 'react';
import {
  X,
  UploadCloud,
  FileText,
  Loader2,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { budgetApi, API_BASE } from '../services/api';
import { Workspace } from '../types/budget';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onWorkspaceCreated: (workspace: Workspace) => void;
}

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi", "Jammu & Kashmir", "Ladakh", "Puducherry", "Chandigarh"
];

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onWorkspaceCreated,
}) => {
  const [govLevel, setGovLevel] = useState<'union' | 'state'>('union');
  const [stateName, setStateName] = useState<string>('Uttar Pradesh');
  const [fy, setFy] = useState<string>('2024-25');
  const [budgetName, setBudgetName] = useState<string>('Union Budget 2024-25');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [uploadStage, setUploadStage] = useState<'idle' | 'creating' | 'uploading' | 'starting'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Health-check the backend when modal opens
  useEffect(() => {
    if (!isOpen) return;
    setBackendOk(null);
    budgetApi.checkHealth()
      .then(() => setBackendOk(true))
      .catch(() => setBackendOk(false));
  }, [isOpen]);

  if (!isOpen) return null;

  const handleGovLevelChange = (level: 'union' | 'state') => {
    setGovLevel(level);
    if (level === 'union') {
      setBudgetName(`Union Budget ${fy}`);
    } else {
      setBudgetName(`${stateName} State Budget ${fy}`);
    }
  };

  const handleStateChange = (st: string) => {
    setStateName(st);
    if (govLevel === 'state') {
      setBudgetName(`${st} State Budget ${fy}`);
    }
  };

  const handleFyChange = (year: string) => {
    setFy(year);
    if (govLevel === 'union') {
      setBudgetName(`Union Budget ${year}`);
    } else {
      setBudgetName(`${stateName} State Budget ${year}`);
    }
  };

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFiles((prev) => [...prev, ...Array.from(e.dataTransfer.files)]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (idx: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFiles.length === 0) {
      setError('Please select at least one budget document to upload.');
      return;
    }

    setIsSubmitting(true);
    setUploadStage('creating');
    setError(null);

    try {
      // 1. Ping backend in background to wake up Render (non-blocking)
      budgetApi.checkHealth().catch(() => {});

      // 2. Create Workspace
      const workspace = await budgetApi.createWorkspace({
        name: budgetName,
        government_level: govLevel,
        state_name: govLevel === 'state' ? stateName : undefined,
        financial_year: fy,
        description: `${govLevel === 'union' ? 'Union Budget of India' : `${stateName} State Budget`} for ${fy}`,
      });

      // 3. Upload Documents
      setUploadStage('uploading');
      await budgetApi.uploadDocuments(workspace.id, selectedFiles);

      // 4. Close modal IMMEDIATELY — user sees dashboard while analysis runs in background
      setUploadStage('starting');
      onWorkspaceCreated(workspace);
      onClose();

      // 5. Fire analysis as non-blocking background job (after modal closed)
      budgetApi.startAnalysis(workspace.id).catch((err) => {
        console.warn('Background analysis start error (non-fatal):', err);
      });

    } catch (err: any) {
      const msg = err.message || 'Failed to upload and initiate budget analysis';
      setError(msg);
      setIsSubmitting(false);
      setUploadStage('idle');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">

        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <UploadCloud className="h-5 w-5 text-blue-400" />
              Upload Budget Documents
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Supports Union &amp; any Indian State budget in PDF, Scanned PDF, Excel, Word, or Image
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto">

          {/* Backend Status Banner */}
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs border ${
            backendOk === null
              ? 'bg-slate-800/50 border-slate-700 text-slate-400'
              : backendOk
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
              : 'bg-red-500/10 border-red-500/20 text-red-300'
          }`}>
            {backendOk === null ? (
              <><Loader2 className="h-3.5 w-3.5 animate-spin shrink-0" /><span>Connecting to backend AI engine at {API_BASE}...</span></>
            ) : backendOk ? (
              <><Wifi className="h-3.5 w-3.5 shrink-0 text-emerald-400" /><span>Backend connected — AI Analysis Engine active at <code className="font-mono bg-emerald-500/10 px-1 rounded">{API_BASE}</code></span></>
            ) : (
              <><WifiOff className="h-3.5 w-3.5 shrink-0 text-amber-400" />
              <span>Connecting to cloud backend at <code className="font-mono bg-amber-500/10 px-1 rounded">{API_BASE}</code>. If Render is waking from sleep, please wait a few seconds and retry.</span></>
            )}
          </div>

          {/* API Error */}
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs flex items-start gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 text-red-400 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Government Level Selection */}
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleGovLevelChange('union')}
              className={`p-3 rounded-xl border text-left transition-all ${
                govLevel === 'union'
                  ? 'border-blue-500 bg-blue-500/10 text-white shadow-sm ring-1 ring-blue-500'
                  : 'border-slate-800 bg-slate-800/50 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Central</div>
              <div className="text-sm font-bold text-white mt-0.5">Union Budget of India</div>
              <div className="text-[11px] text-slate-400 mt-1">Direct/Indirect taxes, Defence, Central Schemes</div>
            </button>

            <button
              type="button"
              onClick={() => handleGovLevelChange('state')}
              className={`p-3 rounded-xl border text-left transition-all ${
                govLevel === 'state'
                  ? 'border-indigo-500 bg-indigo-500/10 text-white shadow-sm ring-1 ring-indigo-500'
                  : 'border-slate-800 bg-slate-800/50 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">State Govt</div>
              <div className="text-sm font-bold text-white mt-0.5">State Budget</div>
              <div className="text-[11px] text-slate-400 mt-1">SGST, State Excise, Devolution, GSDP Deficits</div>
            </button>
          </div>

          {/* State & FY Selectors */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {govLevel === 'state' && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Select State or UT</label>
                <select
                  value={stateName}
                  onChange={(e) => handleStateChange(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {INDIAN_STATES.map((st) => (
                    <option key={st} value={st} className="bg-slate-900">{st}</option>
                  ))}
                </select>
              </div>
            )}

            <div className={govLevel === 'union' ? 'sm:col-span-2' : ''}>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Financial Year</label>
              <input
                type="text"
                value={fy}
                onChange={(e) => handleFyChange(e.target.value)}
                placeholder="e.g. 2024-25, 2023-24"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Workspace Title */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Budget Analysis Workspace Name</label>
            <input
              type="text"
              value={budgetName}
              onChange={(e) => setBudgetName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Drag & Drop File Zone */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Upload Budget Documents</label>
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-6 text-center cursor-pointer bg-slate-800/40 hover:bg-slate-800/80 transition-all group"
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.xlsx,.xls,.csv,.pptx,.jpg,.jpeg,.png,.txt"
                onChange={handleFileSelect}
                className="hidden"
              />
              <div className="mx-auto w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                <UploadCloud className="h-6 w-6" />
              </div>
              <p className="text-sm font-semibold text-slate-200 mt-3">Click to browse or drag &amp; drop documents here</p>
              <p className="text-xs text-slate-400 mt-1">
                Budget Speech, Annual Financial Statement, Demands for Grants, Receipt/Expenditure Budgets (PDF, DOCX, XLSX, Images)
              </p>
            </div>
          </div>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-medium text-slate-300 flex items-center justify-between">
                <span>Selected Documents ({selectedFiles.length})</span>
                <button
                  type="button"
                  onClick={() => setSelectedFiles([])}
                  className="text-slate-400 hover:text-red-400 text-[11px]"
                >
                  Clear all
                </button>
              </div>
              <div className="max-h-40 overflow-y-auto space-y-1.5 pr-1">
                {selectedFiles.map((f, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-2 rounded-lg bg-slate-800/70 border border-slate-700 text-xs"
                  >
                    <div className="flex items-center gap-2 truncate pr-2">
                      <FileText className="h-4 w-4 text-blue-400 shrink-0" />
                      <span className="text-slate-200 font-medium truncate">{f.name}</span>
                      <span className="text-slate-500 text-[11px]">({(f.size / 1024 / 1024).toFixed(2)} MB)</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(i)}
                      className="p-1 text-slate-400 hover:text-red-400 transition-colors"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer Notice */}
          <div className="flex items-center gap-2 text-[11px] text-slate-400 bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
            <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0" />
            <span>
              Deterministic data extraction verifies subtotals, reconciles fiscal deficit equations, and preserves page-level citations.
            </span>
          </div>

          {/* Submit Buttons */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || selectedFiles.length === 0 || backendOk === false}
              className="flex items-center gap-2 px-5 py-2 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white shadow-md shadow-blue-600/30 transition-all"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>
                    {uploadStage === 'creating' ? 'Creating Workspace...' :
                     uploadStage === 'uploading' ? 'Uploading Documents...' :
                     uploadStage === 'starting' ? 'Starting Analysis...' :
                     'Processing...'}
                  </span>
                </>
              ) : (
                <>
                  <span>Start Economic Intelligence</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
