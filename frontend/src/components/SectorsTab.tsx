import React, { useState } from 'react';
import { 
  PieChart as PieIcon, 
  Layers, 
  Search, 
  ChevronRight, 
  TrendingUp, 
  TrendingDown, 
  Sparkles,
  Compass,
  ArrowUpRight
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell 
} from 'recharts';
import { CompleteAnalysis, SectorItem } from '../types/budget';

interface SectorsTabProps {
  data: CompleteAnalysis;
}

const SECTOR_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', 
  '#06b6d4', '#6366f1', '#14b8a6', '#f97316', '#a855f7'
];

export const SectorsTab: React.FC<SectorsTabProps> = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState<SectorItem | null>(null);

  const sectorsObj = data.analysis?.sectors || {};
  const sectorsList: SectorItem[] = sectorsObj.sectors || [];

  const filtered = sectorsList.filter((s) => {
    const name = (s.sector_name || s.name || '').toLowerCase();
    return name.includes(searchTerm.toLowerCase());
  });

  // Top 10 Sectors for Chart
  const chartData = sectorsList.slice(0, 10).map((s) => ({
    name: s.sector_name || s.name || 'Sector',
    allocation: s.allocation || s.total_allocation || 0,
    percentage: s.percentage || s.percentage_of_total || 0,
  }));

  const activeSector = selectedSector || sectorsList[0] || null;

  return (
    <div className="space-y-6">
      
      {/* Header & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Compass className="h-5 w-5 text-blue-400" />
            Sector-Wise Comprehensive Budget Intelligence
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Detailed breakdown of allocations, growth trends, key schemes, and economic impact
          </p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search sectors..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Bar Chart: Top 10 Sectors */}
      {chartData.length > 0 && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
            <Layers className="h-4 w-4 text-blue-400" />
            Top Sectoral Allocations (₹ Crore)
          </h4>
          <p className="text-xs text-slate-400 mb-4">Resource distribution across priority sectors</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 5, right: 20, left: 20, bottom: 25 }}>
                <XAxis 
                  dataKey="name" 
                  stroke="#64748b" 
                  fontSize={10} 
                  angle={-20} 
                  textAnchor="end"
                  interval={0}
                  tickFormatter={(v) => v.length > 15 ? v.substring(0, 13) + '..' : v}
                />
                <YAxis stroke="#64748b" fontSize={10} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k Cr`} />
                <Tooltip
                  formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')} Cr`, 'Allocation']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="allocation" radius={[4, 4, 0, 0]}>
                  {chartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={SECTOR_COLORS[index % SECTOR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Main Split: Sector Selector List + Sector Detail Panel */}
      {sectorsList.length === 0 ? (
        <div className="p-12 text-center text-sm text-slate-500 border border-slate-800 rounded-2xl bg-slate-900">
          No itemized sectoral breakdown was detected in the uploaded document. Please refer to the Overview, Receipts, and Expenditure tabs for aggregate budgetary data.
        </div>
      ) : (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left: Sector Selector List */}
        <div className="lg:col-span-1 space-y-2 max-h-[600px] overflow-y-auto pr-1">
          {filtered.map((sector, idx) => {
            const isSelected = activeSector === sector;
            const name = sector.sector_name || sector.name || 'Sector';
            const alloc = sector.allocation || sector.total_allocation || 0;
            const pct = sector.percentage || sector.percentage_of_total || 0;

            return (
              <div
                key={idx}
                onClick={() => setSelectedSector(sector)}
                className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-500/10 ring-1 ring-blue-500 shadow-md'
                    : 'border-slate-800 bg-slate-900 hover:border-slate-700 hover:bg-slate-850'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-white truncate pr-2">{name}</span>
                  <ChevronRight className={`h-4 w-4 shrink-0 transition-transform ${isSelected ? 'text-blue-400 rotate-90' : 'text-slate-500'}`} />
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="text-slate-400">
                    ₹{alloc ? alloc.toLocaleString('en-IN') : '0'} Cr
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[11px]">
                    {pct}% of Budget
                  </span>
                </div>
              </div>
            );
          })}

          {filtered.length === 0 && (
            <div className="p-8 text-center text-xs text-slate-500 border border-slate-800 rounded-xl bg-slate-900">
              No matching sectors found
            </div>
          )}
        </div>

        {/* Right: Sector Detail Dossier */}
        <div className="lg:col-span-2">
          {activeSector ? (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-5">
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div>
                  <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    Sector Dossier
                  </span>
                  <h3 className="text-xl font-extrabold text-white mt-1">
                    {activeSector.sector_name || activeSector.name}
                  </h3>
                </div>

                <div className="text-right">
                  <div className="text-2xl font-extrabold text-blue-400">
                    ₹{(activeSector.allocation || activeSector.total_allocation || 0).toLocaleString('en-IN')} <span className="text-xs text-slate-400 font-normal">Cr</span>
                  </div>
                  <div className="text-xs text-slate-400">
                    {activeSector.percentage || activeSector.percentage_of_total || 0}% of Total Budget
                  </div>
                </div>
              </div>

              {/* Economic Analysis */}
              <div>
                <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-blue-400" />
                  Policy Impact & Analysis
                </h5>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed bg-slate-800/40 p-3.5 rounded-xl border border-slate-800">
                  {activeSector.analysis ||
                    `Allocation for this sector supports ongoing infrastructure expansion, capacity enhancements, and modernized service delivery. The budgetary provision reinforces grassroots productivity, generates direct and indirect employment, and stimulates private investment in allied value chains.`}
                </p>
              </div>

              {/* Key Schemes in this sector */}
              {activeSector.key_schemes && activeSector.key_schemes.length > 0 && (
                <div>
                  <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Key Programmes & Schemes
                  </h5>
                  <div className="flex flex-wrap gap-2">
                    {activeSector.key_schemes.map((scheme, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs border border-slate-700 flex items-center gap-1.5 font-medium"
                      >
                        <ArrowUpRight className="h-3 w-3 text-emerald-400" />
                        {scheme}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Sector Highlights */}
              {activeSector.highlights && activeSector.highlights.length > 0 && (
                <div>
                  <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Strategic Announcements
                  </h5>
                  <ul className="space-y-1.5">
                    {activeSector.highlights.map((h, i) => (
                      <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0" />
                        <span>{h}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            </div>
          ) : (
            <div className="p-12 text-center text-sm text-slate-500 border border-slate-800 rounded-2xl bg-slate-900">
              Select a sector from the list to view detailed analytical intelligence
            </div>
          )}
        </div>

      </div>
      )}

    </div>
  );
};

