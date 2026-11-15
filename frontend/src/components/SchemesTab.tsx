import React, { useState } from 'react';
import { 
  Award, 
  Search, 
  Users, 
  Target, 
  Building, 
  Sparkles, 
  Tag, 
  ExternalLink,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import { CompleteAnalysis, SchemeItem } from '../types/budget';

interface SchemesTabProps {
  data: CompleteAnalysis;
}

export const SchemesTab: React.FC<SchemesTabProps> = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState<string>('all');

  const schemesObj = data.analysis?.schemes || {};
  const schemesList: SchemeItem[] = schemesObj.schemes || [];

  // Get list of sectors for filter
  const sectors = Array.from(new Set(schemesList.map((s) => s.sector || 'General'))).filter(Boolean);

  const filtered = schemesList.filter((s) => {
    const matchesSearch = (s.scheme_name || s.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.objective || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSector = selectedSector === 'all' || s.sector === selectedSector;
    return matchesSearch && matchesSector;
  });

  return (
    <div className="space-y-6">
      
      {/* Header and Filter Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Award className="h-5 w-5 text-blue-400" />
            Scheme-Wise & Programme Intelligence
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Allocations, policy objectives, and target beneficiaries for all government schemes
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
          {/* Sector Filter */}
          <select
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="w-full sm:w-44 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Sectors ({schemesList.length})</option>
            {sectors.map((sec) => (
              <option key={sec} value={sec}>
                {sec}
              </option>
            ))}
          </select>

          {/* Search Box */}
          <div className="relative w-full sm:w-60">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search schemes..."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Schemes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((scheme, idx) => {
          const name = scheme.scheme_name || scheme.name || 'Scheme';
          const alloc = scheme.current_allocation || scheme.allocation || 0;

          return (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between shadow-sm relative overflow-hidden group"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    {scheme.sector || 'General'}
                  </span>
                  {scheme.is_new && (
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      NEW
                    </span>
                  )}
                </div>

                <h4 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors">
                  {name}
                </h4>

                {scheme.ministry && (
                  <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                    <Building className="h-3 w-3 text-slate-500" />
                    {scheme.ministry}
                  </p>
                )}

                {scheme.objective && (
                  <div className="mt-3 text-xs text-slate-300 leading-relaxed bg-slate-800/40 p-2.5 rounded-lg border border-slate-800/80">
                    <div className="text-[10px] font-semibold text-slate-400 mb-0.5 flex items-center gap-1">
                      <Target className="h-3 w-3 text-blue-400" /> Objective
                    </div>
                    {scheme.objective}
                  </div>
                )}

                {scheme.beneficiaries && (
                  <div className="mt-2 text-xs text-slate-400 flex items-center gap-1.5">
                    <Users className="h-3.5 w-3.5 text-indigo-400 shrink-0" />
                    <span className="truncate">Beneficiaries: {scheme.beneficiaries}</span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-400 block">Outlay</span>
                  <span className="text-sm font-bold text-emerald-400">
                    ₹{alloc ? alloc.toLocaleString('en-IN') : '0'} Cr
                  </span>
                </div>

                {scheme.previous_allocation && (
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block">Previous</span>
                    <span className="text-xs text-slate-300">
                      ₹{scheme.previous_allocation.toLocaleString('en-IN')} Cr
                    </span>
                  </div>
                )}
              </div>

            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="col-span-full p-12 text-center text-sm text-slate-500 border border-slate-800 rounded-xl bg-slate-900">
            {schemesList.length === 0 
              ? "No itemized government schemes or flagship programmes were identified in this uploaded document. Review the Overview and Expenditure tabs for aggregate allocations." 
              : "No schemes found matching the current search and filter criteria."}
          </div>
        )}
      </div>

    </div>
  );
};

