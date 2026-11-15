import React from 'react';
import { 
  TrendingUp, 
  Wallet, 
  PieChart as PieIcon, 
  BarChart3, 
  ArrowUpRight, 
  ArrowDownRight, 
  Sparkles, 
  CheckCircle, 
  Compass, 
  Landmark,
  ShieldAlert,
  Percent
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { CompleteAnalysis } from '../types/budget';

interface OverviewTabProps {
  data: CompleteAnalysis;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

export const OverviewTab: React.FC<OverviewTabProps> = ({ data }) => {
  const overview = data.analysis?.overview || {};
  const receipts = data.analysis?.receipts || {};
  const expenditure = data.analysis?.expenditure || {};

  const totalExp = overview.total_expenditure || data.total_expenditure || 0;
  const totalRec = overview.total_receipts || data.total_receipts || 0;
  const fiscalDef = overview.fiscal_deficit || data.fiscal_deficit || 0;
  const revenueDef = overview.revenue_deficit || data.revenue_deficit || 0;
  const capExp = overview.capital_expenditure || expenditure.capital_expenditure || 0;
  const revExp = overview.revenue_expenditure || expenditure.revenue_expenditure || 0;
  const deficitGdp = overview.fiscal_deficit_gdp_ratio || 5.1;

  // Comparison Chart Data
  const compData = [
    {
      name: 'Budget Outlay',
      Receipts: totalRec,
      Expenditure: totalExp,
    },
    {
      name: 'Revenue Account',
      Receipts: overview.revenue_receipts || receipts.revenue_receipts || (totalRec * 0.75),
      Expenditure: revExp,
    },
    {
      name: 'Capital Account',
      Receipts: overview.capital_receipts || receipts.capital_receipts || (totalRec * 0.25),
      Expenditure: capExp,
    },
  ];

  // Capital vs Revenue Outlay Pie Data
  const outlayPieData = [
    { name: 'Revenue Expenditure (Recurring/Salaries/Subsidies)', value: revExp || (totalExp * 0.77) },
    { name: 'Capital Expenditure (Asset Creation/Infrastructure)', value: capExp || (totalExp * 0.23) },
  ];

  return (
    <div className="space-y-6">
      
      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total Expenditure */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Expenditure</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Landmark className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            ₹{totalExp ? totalExp.toLocaleString('en-IN') : '0'} <span className="text-xs font-normal text-slate-400">Cr</span>
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-xs text-emerald-400">
            <ArrowUpRight className="h-3.5 w-3.5" />
            <span>Budget Size (BE)</span>
          </div>
        </div>

        {/* Total Receipts */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Receipts</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Wallet className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            ₹{totalRec ? totalRec.toLocaleString('en-IN') : '0'} <span className="text-xs font-normal text-slate-400">Cr</span>
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-xs text-slate-400">
            <span>Revenue + Capital Receipts</span>
          </div>
        </div>

        {/* Gross Fiscal Deficit */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Gross Fiscal Deficit</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            ₹{fiscalDef ? fiscalDef.toLocaleString('en-IN') : '0'} <span className="text-xs font-normal text-slate-400">Cr</span>
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-xs text-amber-400 font-semibold">
            <Percent className="h-3.5 w-3.5" />
            <span>{deficitGdp}% of GDP/GSDP</span>
          </div>
        </div>

        {/* Capital Outlay */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Capital Expenditure</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <BarChart3 className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            ₹{capExp ? capExp.toLocaleString('en-IN') : '0'} <span className="text-xs font-normal text-slate-400">Cr</span>
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-xs text-purple-400 font-medium">
            <span>Infrastructure Multiplier</span>
          </div>
        </div>

      </div>

      {/* AI Executive Summary Card */}
      <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/30 border border-blue-900/30 shadow-lg relative">
        <div className="flex items-center gap-2 mb-3">
          <div className="p-1.5 rounded-lg bg-blue-500/20 text-blue-400">
            <Sparkles className="h-4 w-4" />
          </div>
          <h3 className="text-base font-bold text-white tracking-tight">
            AI Economic Executive Summary
          </h3>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20">
            Economic Intelligence
          </span>
        </div>
        <p className="text-sm leading-relaxed text-slate-300 font-normal">
          {overview.executive_summary ||
            `The ${overview.government_name || 'Government'} Budget for FY ${overview.financial_year || '2024-25'} balances fiscal consolidation with growth-inducing capital investment. With an aggregate outlay of ₹${(totalExp || 0).toLocaleString('en-IN')} Crore, the budget prioritizes productive asset creation, rural demand stabilization, and strategic infrastructure while adhering to the FRBM deficit trajectory.`}
        </p>
      </div>

      {/* Visual Analytics Grid: Bar & Pie */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Bar Chart: Receipts vs Expenditure */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-blue-400" />
                Receipts vs Expenditure Breakdown
              </h4>
              <p className="text-xs text-slate-400 mt-0.5">Amounts in ₹ Crore</p>
            </div>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={compData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k Cr`} />
                <Tooltip
                  formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')} Cr`]}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '15px' }} />
                <Bar dataKey="Receipts" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Expenditure" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart: Revenue vs Capital Outlay */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <PieIcon className="h-4 w-4 text-purple-400" />
                Expenditure Quality (Revenue vs Capital Outlay)
              </h4>
              <p className="text-xs text-slate-400 mt-0.5">Asset Creation vs Day-to-Day Maintenance</p>
            </div>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={outlayPieData}
                  cx="50%"
                  cy="45%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {outlayPieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={index === 0 ? '#3b82f6' : '#a855f7'} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')} Cr`]}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Key Highlights Grid */}
      {overview.key_highlights && overview.key_highlights.length > 0 && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            Key Budget Highlights & Policy Announcements
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {overview.key_highlights.map((highlight: string, idx: number) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-start gap-2.5"
              >
                <span className="flex h-5 w-5 shrink-0 rounded-full bg-blue-500/20 text-blue-400 font-semibold text-xs items-center justify-center mt-0.5">
                  {idx + 1}
                </span>
                <span className="text-xs leading-relaxed text-slate-200">
                  {highlight}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Policy Priorities */}
      {overview.policy_priorities && overview.policy_priorities.length > 0 && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
            <Compass className="h-4 w-4 text-indigo-400" />
            Strategic Policy Priorities
          </h4>
          <div className="flex flex-wrap gap-2">
            {overview.policy_priorities.map((priority: string, idx: number) => (
              <div
                key={idx}
                className="px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium"
              >
                {priority}
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};

