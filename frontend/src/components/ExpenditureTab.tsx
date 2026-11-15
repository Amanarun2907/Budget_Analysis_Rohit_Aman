import React from 'react';
import { 
  Building2, 
  Layers, 
  BarChart3, 
  Coins, 
  Shield, 
  Wheat, 
  TrendingUp,
  PieChart as PieIcon,
  Sparkles
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
import { CompleteAnalysis } from '../types/budget';

interface ExpenditureTabProps {
  data: CompleteAnalysis;
}

const BAR_COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#10b981', '#06b6d4'];

export const ExpenditureTab: React.FC<ExpenditureTabProps> = ({ data }) => {
  const exp = data.analysis?.expenditure || {};
  const overview = data.analysis?.overview || {};

  const totalExp = exp.total_expenditure || overview.total_expenditure || 0;
  const revExp = exp.revenue_expenditure || overview.revenue_expenditure || 0;
  const capExp = exp.capital_expenditure || overview.capital_expenditure || 0;

  // Top Ministries Data (only from verified extracted analysis)
  const ministries: Array<{ name: string; allocation: number; percentage?: number }> = 
    (exp.top_spending_ministries && exp.top_spending_ministries.length > 0)
      ? exp.top_spending_ministries
      : (exp.ministry_wise && exp.ministry_wise.length > 0)
      ? exp.ministry_wise
      : [];

  return (
    <div className="space-y-6">
      
      {/* Top Level Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Expenditure</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Building2 className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {totalExp ? `₹${totalExp.toLocaleString('en-IN')} ` : <span className="text-slate-500 text-base font-medium">Not specified</span>}<span className="text-xs font-normal text-slate-400">{totalExp ? 'Cr' : ''}</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">
            Combined Revenue + Capital Outlay
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Revenue Expenditure (Maintenance)</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Layers className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {revExp ? `₹${revExp.toLocaleString('en-IN')} ` : <span className="text-slate-500 text-base font-medium">Not specified</span>}<span className="text-xs font-normal text-slate-400">{revExp ? 'Cr' : ''}</span>
          </div>
          <div className="mt-1 text-xs text-indigo-400 font-medium">
            {totalExp && revExp ? `${((revExp / totalExp) * 100).toFixed(1)}% of Budget (Operational & Service Commitments)` : 'Operational & Service Commitments'}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Capital Outlay (Asset Creation)</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {capExp ? `₹${capExp.toLocaleString('en-IN')} ` : <span className="text-slate-500 text-base font-medium">Not specified</span>}<span className="text-xs font-normal text-slate-400">{capExp ? 'Cr' : ''}</span>
          </div>
          <div className="mt-1 text-xs text-purple-400 font-medium">
            {totalExp && capExp ? `${((capExp / totalExp) * 100).toFixed(1)}% of Budget (Productive Capex)` : 'Productive Capex'}
          </div>
        </div>

      </div>

      {/* Top Spending Ministries Chart */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-blue-400" />
              Top Spending Ministries & Departments
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">Allocations in ₹ Crore and Percentage Share of Budget</p>
          </div>
        </div>

        <div className="h-80 w-full mt-4">
          {ministries.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={ministries.slice(0, 10)}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 30, bottom: 5 }}
              >
                <XAxis type="number" stroke="#64748b" fontSize={10} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k Cr`} />
                <YAxis
                  dataKey="name"
                  type="category"
                  stroke="#64748b"
                  fontSize={11}
                  width={180}
                  tickFormatter={(v) => v.length > 28 ? v.substring(0, 26) + '...' : v}
                />
                <Tooltip
                  formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')} Cr`, 'Allocation']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="allocation" radius={[0, 4, 4, 0]}>
                  {ministries.slice(0, 10).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-500">
              Department/Ministry itemized allocations not found in uploaded document
            </div>
          )}
        </div>
      </div>

      {/* Committed Expenditure Cards */}
      {(exp.interest_payments != null || exp.subsidies != null || exp.defence_expenditure != null) && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
            <Coins className="h-4 w-4 text-amber-400" />
            Major Committed &amp; Non-Discretionary Expenditures
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            
            {exp.interest_payments != null && (
              <div className="p-3.5 rounded-lg bg-slate-800/60 border border-slate-700/60">
                <span className="text-xs text-slate-400">Interest Payments</span>
                <div className="text-lg font-bold text-white mt-1">
                  ₹{Number(exp.interest_payments).toLocaleString('en-IN')} Cr
                </div>
                <span className="text-[11px] text-slate-400">Debt servicing liability</span>
              </div>
            )}

            {exp.subsidies != null && (
              <div className="p-3.5 rounded-lg bg-slate-800/60 border border-slate-700/60">
                <span className="text-xs text-slate-400">Subsidies (Food, Fert, Fuel)</span>
                <div className="text-lg font-bold text-white mt-1">
                  ₹{Number(exp.subsidies).toLocaleString('en-IN')} Cr
                </div>
                <span className="text-[11px] text-slate-400">Targeted welfare transfers</span>
              </div>
            )}

            {exp.defence_expenditure != null && (
              <div className="p-3.5 rounded-lg bg-slate-800/60 border border-slate-700/60">
                <span className="text-xs text-slate-400">Defence Outlay</span>
                <div className="text-lg font-bold text-white mt-1">
                  ₹{Number(exp.defence_expenditure).toLocaleString('en-IN')} Cr
                </div>
                <span className="text-[11px] text-slate-400">Modernization + Operational</span>
              </div>
            )}

          </div>
        </div>
      )}

      {/* Analytical Narrative */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-2">
          <Sparkles className="h-4 w-4 text-blue-400" />
          Expenditure Quality & Capital Investment Analysis
        </h4>
        {exp.analysis_text ? (
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">{exp.analysis_text}</p>
        ) : (
          <p className="text-xs text-slate-500 italic">Expenditure quality analysis narrative was not extracted from this document.</p>
        )}
      </div>

    </div>
  );
};

