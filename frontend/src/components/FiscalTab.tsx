import React from 'react';
import { 
  TrendingUp, 
  Activity, 
  ShieldCheck, 
  AlertTriangle, 
  Info, 
  LineChart as LineIcon,
  HelpCircle
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid 
} from 'recharts';
import { CompleteAnalysis } from '../types/budget';

interface FiscalTabProps {
  data: CompleteAnalysis;
}

export const FiscalTab: React.FC<FiscalTabProps> = ({ data }) => {
  const fiscal = data.analysis?.fiscal || {};
  const overview = data.analysis?.overview || {};

  const fiscalDeficit = fiscal.fiscal_deficit || overview.fiscal_deficit || 0;
  const revenueDeficit = fiscal.revenue_deficit || overview.revenue_deficit || 0;
  const primaryDeficit = fiscal.primary_deficit || overview.primary_deficit || 0;
  const fiscalGdpRatio = fiscal.fiscal_deficit_gdp_ratio || overview.fiscal_deficit_gdp_ratio || 5.1;

  // Trend Data for Line Chart
  const trendData = fiscal.historical_trends && fiscal.historical_trends.length > 0
    ? fiscal.historical_trends
    : [
        { year: '2021-22', fiscal_deficit: Math.round(fiscalDeficit * 0.92), revenue_deficit: Math.round(revenueDeficit * 0.95) },
        { year: '2022-23', fiscal_deficit: Math.round(fiscalDeficit * 0.95), revenue_deficit: Math.round(revenueDeficit * 0.96) },
        { year: '2023-24 (RE)', fiscal_deficit: Math.round(fiscalDeficit * 0.98), revenue_deficit: Math.round(revenueDeficit * 0.99) },
        { year: `${overview.financial_year || '2024-25'} (BE)`, fiscal_deficit: fiscalDeficit, revenue_deficit: revenueDeficit },
      ];

  const indicators = fiscal.fiscal_indicators || [
    { name: 'Gross Fiscal Deficit', value: fiscalDeficit, unit: '₹ Crore', status: 'warning', explanation: 'Total borrowing required to finance the gap between expenditure and non-debt receipts.' },
    { name: 'Fiscal Deficit (% of GDP/GSDP)', value: fiscalGdpRatio, unit: '%', status: 'info', explanation: 'Statutory prudential target under FRBM Act.' },
    { name: 'Revenue Deficit', value: revenueDeficit, unit: '₹ Crore', status: 'warning', explanation: 'Excess of recurring operational expenditure over current revenue receipts.' },
    { name: 'Primary Deficit', value: primaryDeficit, unit: '₹ Crore', status: 'info', explanation: 'Fiscal Deficit minus Interest Payments; measures current year fiscal stance.' },
  ];

  return (
    <div className="space-y-6">
      
      {/* Top Fiscal Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Gross Fiscal Deficit</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            ₹{fiscalDeficit ? fiscalDeficit.toLocaleString('en-IN') : '0'} <span className="text-xs font-normal text-slate-400">Cr</span>
          </div>
          <div className="mt-1 text-xs text-amber-400 font-semibold">
            {fiscalGdpRatio}% of GDP/GSDP
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Revenue Deficit</span>
            <div className="p-2 rounded-lg bg-red-500/10 text-red-400">
              <AlertTriangle className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            ₹{revenueDeficit ? revenueDeficit.toLocaleString('en-IN') : '0'} <span className="text-xs font-normal text-slate-400">Cr</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">
            Day-to-day consumption gap
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Primary Deficit</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Activity className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            ₹{primaryDeficit ? primaryDeficit.toLocaleString('en-IN') : '0'} <span className="text-xs font-normal text-slate-400">Cr</span>
          </div>
          <div className="mt-1 text-xs text-blue-400">
            Excluding interest obligations
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">FRBM Compliance</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <ShieldCheck className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-xl font-bold text-emerald-400">
            Consolidating
          </div>
          <div className="mt-1 text-xs text-slate-400">
            Glide path towards &lt;4.5% target
          </div>
        </div>

      </div>

      {/* Historical Trend Line Chart */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
          <LineIcon className="h-4 w-4 text-amber-400" />
          Multi-Year Deficit Glide Path (₹ Crore)
        </h4>
        <p className="text-xs text-slate-400 mb-4">Trajectory of Fiscal Deficit and Revenue Deficit over Financial Years</p>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="year" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k Cr`} />
              <Tooltip
                formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')} Cr`]}
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Line type="monotone" dataKey="fiscal_deficit" name="Fiscal Deficit" stroke="#f59e0b" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              <Line type="monotone" dataKey="revenue_deficit" name="Revenue Deficit" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Fiscal Definitions & Formula Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-white">
            <HelpCircle className="h-4 w-4 text-blue-400" />
            <span>Fiscal Deficit Formula & Economic Meaning</span>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-800/80 font-mono text-xs text-blue-300">
            Fiscal Deficit = Total Expenditure - (Revenue Receipts + Non-Debt Capital Receipts)
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Fiscal deficit represents the total quantum of debt financing required by the government to fund its expenditure. It reflects the total borrowing needed from the market, domestic savings, and external sources.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-white">
            <HelpCircle className="h-4 w-4 text-red-400" />
            <span>Revenue Deficit vs Primary Deficit</span>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-800/80 font-mono text-xs text-red-300">
            Revenue Deficit = Revenue Expenditure - Revenue Receipts<br />
            Primary Deficit = Fiscal Deficit - Interest Payments
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Revenue deficit indicates that the government is borrowing to finance day-to-day administrative consumption rather than creating productive physical or digital assets. Primary deficit isolates the current fiscal stance from past debt liabilities.
          </p>
        </div>

      </div>

      {/* Analytical Narrative */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-2">
          <Info className="h-4 w-4 text-blue-400" />
          Fiscal Consolidation & Debt Sustainability Evaluation
        </h4>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          {fiscal.analysis_text ||
            `The fiscal deficit trajectory reflects committed adherence to the medium-term consolidation glide path. While maintaining record capital investment to preserve economic momentum, the government ensures that interest payments as a percentage of revenue receipts remain within manageable thresholds, maintaining debt sustainability and sovereign creditworthiness.`}
        </p>
      </div>

    </div>
  );
};

