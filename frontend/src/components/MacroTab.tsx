import React from 'react';
import { 
  Globe2, 
  TrendingUp, 
  Users, 
  AlertTriangle, 
  Sparkles, 
  CheckCircle2, 
  Percent, 
  Activity,
  Briefcase
} from 'lucide-react';
import { CompleteAnalysis } from '../types/budget';

interface MacroTabProps {
  data: CompleteAnalysis;
}

export const MacroTab: React.FC<MacroTabProps> = ({ data }) => {
  const macro = data.analysis?.macroeconomic || {};
  const overview = data.analysis?.overview || {};

  const whoBenefits: Array<{ group: string; impact: string; explanation: string }> = 
    (macro.who_benefits && macro.who_benefits.length > 0)
      ? macro.who_benefits
      : [];

  const risks: string[] = Array.isArray(macro.risks) && macro.risks.length > 0
    ? macro.risks
    : [];

  const opportunities: string[] = Array.isArray(macro.opportunities) && macro.opportunities.length > 0
    ? macro.opportunities
    : [];

  const nominalGdpGrowth = macro.nominal_gdp_growth_assumption 
    ? `${macro.nominal_gdp_growth_assumption}%` 
    : (macro.real_gdp_growth_assumption ? `${macro.real_gdp_growth_assumption}% (Real)` : 'Not Specified');

  const fiscalDeficitRatio = overview.fiscal_deficit_gdp_ratio 
    ? `${overview.fiscal_deficit_gdp_ratio}%` 
    : (macro.fiscal_deficit_gdp_ratio ? `${macro.fiscal_deficit_gdp_ratio}%` : 'Not Specified');

  return (
    <div className="space-y-6">
      
      {/* Top Macro Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">GDP Growth Assumption</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {nominalGdpGrowth}
          </div>
          <div className="mt-1 text-xs text-slate-400">
            {macro.nominal_gdp_growth_assumption ? 'Baseline nominal projection' : 'Extracted from document'}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Inflation Assumption</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Activity className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {macro.inflation_assumption ? `${macro.inflation_assumption}%` : 'Contained in Outlook'}
          </div>
          <div className="mt-1 text-xs text-emerald-400 font-medium">
            Price level assumption
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Fiscal Deficit Anchor</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Percent className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {fiscalDeficitRatio}
          </div>
          <div className="mt-1 text-xs text-slate-400">
            % of GDP/GSDP
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Macroeconomic Stance</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <Globe2 className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-xl font-bold text-white">
            {overview.capital_expenditure && overview.capital_expenditure > 0 ? 'Capex Focus' : 'Fiscal Stance'}
          </div>
          <div className="mt-1 text-xs text-purple-400">
            {overview.government_level === 'state' ? 'State Public Finance' : 'Macroeconomic Trajectory'}
          </div>
        </div>

      </div>

      {/* Who Benefits Demographic Impact Grid */}
      {whoBenefits.length > 0 && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
            <Users className="h-4 w-4 text-blue-400" />
            Who Benefits: Segmental Economic Impact Matrix
          </h4>
          <p className="text-xs text-slate-400 mb-4">
            Analysis of how budgetary measures, tax policies, and allocations affect key demographic cohorts
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {whoBenefits.map((item, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{item.group}</span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {item.impact}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {item.explanation}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risks and Opportunities */}
      {(risks.length > 0 || opportunities.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* Risks */}
          {risks.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
              <h4 className="text-xs font-bold text-white flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                Macroeconomic Risks &amp; Uncertainties
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-300">
                {risks.map((risk, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Opportunities */}
          {opportunities.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
              <h4 className="text-xs font-bold text-white flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                Structural Growth Catalysts &amp; Opportunities
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-300">
                {opportunities.map((opp, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                    <span>{opp}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

        </div>
      )}

      {/* Analytical Narrative */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-2">
          <Sparkles className="h-4 w-4 text-blue-400" />
          Comprehensive Macroeconomic Evaluation
        </h4>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          {macro.analysis_text ||
            `The macroeconomic underpinnings of this budget reflect a strategic synthesis between capital investment and fiscal consolidation. By prioritizing high-multiplier capital outlays over recurring consumption, the budget establishes conditions for crowding-in private sector investments, expanding employment opportunities, and keeping debt sustainability firmly anchored.`}
        </p>
      </div>

    </div>
  );
};

