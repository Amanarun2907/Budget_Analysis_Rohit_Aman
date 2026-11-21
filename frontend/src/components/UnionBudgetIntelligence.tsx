import React, { useState, useEffect } from 'react';
import {
  Landmark,
  ArrowRightLeft,
  History,
  Sliders,
  Calculator,
  BookOpen,
  PieChart as PieIcon,
  TrendingUp,
  Percent,
  Wallet,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Sparkles,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Share2,
  RefreshCw,
  Coins
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Cell,
  PieChart,
  Pie
} from 'recharts';
import { budgetApi } from '../services/api';

type SubView = 'flows' | 'historical' | 'simulator' | 'subsidies' | 'devolution' | 'tax_calc' | 'upsc';

export const UnionBudgetIntelligence: React.FC = () => {
  const [activeSubView, setActiveSubView] = useState<SubView>('flows');
  const [overviewData, setOverviewData] = useState<any>(null);
  const [upscData, setUpscData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // What-If Simulator state
  const [gdpGrowth, setGdpGrowth] = useState<number>(10.5);
  const [oilPrice, setOilPrice] = useState<number>(80.0);
  const [disinvestPct, setDisinvestPct] = useState<number>(100.0);
  const [taxBuoyancy, setTaxBuoyancy] = useState<number>(1.1);
  const [simResults, setSimResults] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Tax Calculator state
  const [grossIncome, setGrossIncome] = useState<number>(1200000);
  const [sec80c, setSec80c] = useState<number>(150000);
  const [sec80d, setSec80d] = useState<number>(25000);
  const [hra, setHra] = useState<number>(0);
  const [taxCalcResult, setTaxCalcResult] = useState<any>(null);

  // State search
  const [stateSearch, setStateSearch] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    runSimulator();
  }, [gdpGrowth, oilPrice, disinvestPct, taxBuoyancy]);

  useEffect(() => {
    runTaxCalculator();
  }, [grossIncome, sec80c, sec80d, hra]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const ov = await budgetApi.getUnionIntelligenceOverview();
      setOverviewData(ov);
      const up = await budgetApi.getUPSCInsights();
      setUpscData(up);
    } catch (err) {
      console.error('Failed to load Union Intelligence overview:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const runSimulator = async () => {
    setIsSimulating(true);
    try {
      const res = await budgetApi.runWhatIfSimulation({
        nominal_gdp_growth_pct: gdpGrowth,
        crude_oil_price_usd: oilPrice,
        disinvestment_realization_pct: disinvestPct,
        tax_buoyancy: taxBuoyancy,
      });
      setSimResults(res);
    } catch (err) {
      console.error('Simulator error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  const runTaxCalculator = async () => {
    try {
      const res = await budgetApi.calculateTaxRegimes({
        gross_annual_income: grossIncome,
        sec_80c_investment: sec80c,
        sec_80d_health: sec80d,
        hra_exemption: hra,
      });
      setTaxCalcResult(res);
    } catch (err) {
      console.error('Tax calculator error:', err);
    }
  };

  const subNavItems = [
    { id: 'flows', label: 'Rupee Flows (Sankey Breakdown)', icon: ArrowRightLeft },
    { id: 'historical', label: '10-Year Historical (BE vs RE vs Actuals)', icon: History },
    { id: 'simulator', label: 'What-If Economic Simulator', icon: Sliders },
    { id: 'subsidies', label: 'Subsidies & Rationalization', icon: Wallet },
    { id: 'devolution', label: '15th FC State Devolution', icon: Landmark },
    { id: 'tax_calc', label: 'Tax Regime Comparison Calculator', icon: Calculator },
    { id: 'upsc', label: 'UPSC & Constitutional Guide', icon: BookOpen },
  ];

  const historicalChartData = (overviewData?.historical_series || []).map((h: any) => ({
    year: h.year,
    'Budget Estimate (BE)': h.be_exp,
    'Actual Expenditure': h.actual_exp,
    'Capital Outlay (Capex)': h.capex,
    'Fiscal Deficit % GDP': h.fiscal_def_pct,
  }));

  const subsidiesChartData = (overviewData?.subsidies || []).map((s: any) => ({
    year: s.year,
    'Food Subsidy': s.food,
    'Fertilizer Subsidy': s.fertilizer,
    'Petroleum Subsidy': s.petroleum,
  }));

  const filteredStates = (overviewData?.state_devolution || []).filter((s: any) =>
    s.state.toLowerCase().includes(stateSearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      
      {/* Hero Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border border-blue-500/30 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs uppercase tracking-widest font-black px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Official Government Public Finance Analytics
              </span>
              <span className="text-xs text-slate-400">• 10-Year Longitudinal Analysis</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Union Budget Deep Intelligence &amp; Macroeconomic Sandbox
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
              Exhaustive analysis of Union Government of India public finances: 10-year BE vs RE vs Actuals trends,
              Rupee flow decompositions, interactive economic policy simulators, and 15th Finance Commission devolution matrix.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={loadData}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/30 transition-all"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Refresh Datasets</span>
            </button>
          </div>
        </div>

        {/* Top KPI Ribbon */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 mt-6 pt-5 border-t border-slate-800/80">
          <div>
            <div className="text-[11px] text-slate-400">Total Budget (BE 2024-25)</div>
            <div className="text-lg font-black text-white font-mono">₹48,20,512 Cr</div>
          </div>
          <div>
            <div className="text-[11px] text-slate-400">Capital Outlay (Capex)</div>
            <div className="text-lg font-black text-purple-400 font-mono">₹11,11,111 Cr</div>
          </div>
          <div>
            <div className="text-[11px] text-slate-400">10-Year Capex CAGR</div>
            <div className="text-lg font-black text-emerald-400 font-mono">+18.91%</div>
          </div>
          <div>
            <div className="text-[11px] text-slate-400">Fiscal Deficit Target</div>
            <div className="text-lg font-black text-amber-400 font-mono">4.9% of GDP</div>
          </div>
          <div>
            <div className="text-[11px] text-slate-400">State Devolution Pool</div>
            <div className="text-lg font-black text-blue-400 font-mono">₹9,64,102 Cr</div>
          </div>
          <div>
            <div className="text-[11px] text-slate-400">Subsidies as % of GDP</div>
            <div className="text-lg font-black text-cyan-400 font-mono">1.17% (Rationalized)</div>
          </div>
        </div>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 no-scrollbar">
        {subNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSubView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveSubView(item.id as SubView)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30 ring-1 ring-blue-400'
                  : 'bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Sub-View Content */}

      {/* 1. Rupee Flows Breakdown (Where Rupee Comes From & Goes To) */}
      {activeSubView === 'flows' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Where Rupee Comes From */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                    <ArrowDownRight className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Where Rupee Comes From (Inflows)</h3>
                    <p className="text-xs text-slate-400">Share in every 100 paise collected</p>
                  </div>
                </div>
                <span className="text-xs font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded">
                  100 Paise Total
                </span>
              </div>

              <div className="space-y-2.5">
                {(overviewData?.rupee_flows?.comes_from || []).map((item: any, idx: number) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-200">{item.source}</span>
                      <span className="font-mono font-bold text-emerald-400">{item.share_paise}p ({item.share_paise}%)</span>
                    </div>
                    <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-emerald-500 h-full rounded-full"
                        style={{ width: `${item.share_paise}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span>Category: {item.category}</span>
                      <span className="font-mono">₹{item.amount_cr.toLocaleString()} Cr</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Where Rupee Goes To */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                    <ArrowUpRight className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Where Rupee Goes To (Outflows)</h3>
                    <p className="text-xs text-slate-400">Share in every 100 paise allocated</p>
                  </div>
                </div>
                <span className="text-xs font-mono text-blue-400 font-bold bg-blue-500/10 px-2 py-0.5 rounded">
                  100 Paise Total
                </span>
              </div>

              <div className="space-y-2.5">
                {(overviewData?.rupee_flows?.goes_to || []).map((item: any, idx: number) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-200">{item.destination}</span>
                      <span className="font-mono font-bold text-blue-400">{item.share_paise}p ({item.share_paise}%)</span>
                    </div>
                    <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-blue-500 h-full rounded-full"
                        style={{ width: `${item.share_paise}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span>Category: {item.category}</span>
                      <span className="font-mono">₹{item.amount_cr.toLocaleString()} Cr</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* 2. 10-Year Historical Trends (BE vs RE vs Actuals) */}
      {activeSubView === 'historical' && (
        <div className="space-y-6">
          
          {/* Capex Multiplier Trend */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-purple-400" />
                  10-Year Capital Outlay Surge (FY15 to FY25)
                </h3>
                <p className="text-xs text-slate-400">
                  Capital expenditure surged from ₹1.96 Lakh Crore in FY15 to ₹11.11 Lakh Crore in FY25 (18.91% CAGR)
                </p>
              </div>
              <span className="text-xs font-mono text-purple-400 bg-purple-500/10 px-2.5 py-1 rounded-lg border border-purple-500/20">
                Capex Multiplier: 3.1x Output Growth
              </span>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={historicalChartData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                  <XAxis dataKey="year" stroke="#64748b" fontSize={11} angle={-25} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `₹${(v/100000).toFixed(1)}L Cr`} />
                  <Tooltip
                    formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')} Crore`]}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Bar dataKey="Capital Outlay (Capex)" fill="#a855f7" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Budget Estimate (BE)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Fiscal Deficit Trajectory (% of GDP) */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Percent className="h-4 w-4 text-amber-400" />
                  Fiscal Deficit Trajectory (% of GDP) &amp; Consolidation Glide Path
                </h3>
                <p className="text-xs text-slate-400">
                  Steep pandemic shock (9.2% in FY21) successfully consolidated down to 4.9% (FY25 target &lt;4.5% by FY26)
                </p>
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historicalChartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                  <XAxis dataKey="year" stroke="#64748b" fontSize={11} angle={-25} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={11} domain={[2, 10]} tickFormatter={(v) => `${v}%`} />
                  <Tooltip
                    formatter={(val: any) => [`${val}% of GDP`]}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Line type="monotone" dataKey="Fiscal Deficit % GDP" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Historical Data Table */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <h3 className="text-sm font-bold text-white">Longitudinal Historical Public Finance Table (₹ Crore)</h3>
            <div className="overflow-x-auto no-scrollbar">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-800/70 text-slate-400 uppercase text-[10px]">
                  <tr>
                    <th className="p-2.5">Financial Year</th>
                    <th className="p-2.5">Budget Estimate</th>
                    <th className="p-2.5">Revised Estimate</th>
                    <th className="p-2.5">Actual Expenditure</th>
                    <th className="p-2.5">Capital Outlay</th>
                    <th className="p-2.5">Fiscal Deficit %</th>
                    <th className="p-2.5">Nominal GDP</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-200 font-mono">
                  {(overviewData?.historical_series || []).map((row: any, i: number) => (
                    <tr key={i} className="hover:bg-slate-800/40">
                      <td className="p-2.5 font-bold text-white">{row.year}</td>
                      <td className="p-2.5">₹{row.be_exp.toLocaleString()}</td>
                      <td className="p-2.5">₹{row.re_exp.toLocaleString()}</td>
                      <td className="p-2.5 text-blue-400 font-semibold">{row.actual_exp ? `₹${row.actual_exp.toLocaleString()}` : 'Awaiting CGA'}</td>
                      <td className="p-2.5 text-purple-400 font-semibold">₹{row.capex.toLocaleString()}</td>
                      <td className="p-2.5 text-amber-400 font-semibold">{row.fiscal_def_pct}%</td>
                      <td className="p-2.5 text-slate-400">₹{row.nominal_gdp.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

      {/* 3. What-If Economic Policy Simulator */}
      {activeSubView === 'simulator' && (
        <div className="space-y-6">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sliders className="h-4 w-4 text-blue-400" />
                Macroeconomic Sensitivity &amp; What-If Scenario Sandbox
              </h3>
              <p className="text-xs text-slate-400">
                Adjust economic policy parameters to observe live simulated impacts on India's fiscal deficit, tax receipts, and budget outlays.
              </p>
            </div>

            {/* Sliders Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
              
              {/* GDP Growth */}
              <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-semibold">Nominal GDP Growth</span>
                  <span className="font-mono font-bold text-blue-400">{gdpGrowth}%</span>
                </div>
                <input
                  type="range"
                  min="6.0"
                  max="16.0"
                  step="0.25"
                  value={gdpGrowth}
                  onChange={(e) => setGdpGrowth(parseFloat(e.target.value))}
                  className="w-full accent-blue-500 cursor-pointer"
                />
                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span>6.0% (Bearish)</span>
                  <span>10.5% (Budget BE)</span>
                  <span>16.0% (Bullish)</span>
                </div>
              </div>

              {/* Crude Oil Price */}
              <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-semibold">Brent Crude Oil</span>
                  <span className="font-mono font-bold text-amber-400">${oilPrice}/bbl</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="130"
                  step="2"
                  value={oilPrice}
                  onChange={(e) => setOilPrice(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer"
                />
                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span>$50 (Deflationary)</span>
                  <span>$80 (Base)</span>
                  <span>$130 (Shock)</span>
                </div>
              </div>

              {/* Disinvestment Realization */}
              <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-semibold">Disinvestment Target %</span>
                  <span className="font-mono font-bold text-purple-400">{disinvestPct}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="150"
                  step="5"
                  value={disinvestPct}
                  onChange={(e) => setDisinvestPct(parseFloat(e.target.value))}
                  className="w-full accent-purple-500 cursor-pointer"
                />
                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span>0% (Slippage)</span>
                  <span>100% (Target)</span>
                  <span>150% (Surplus)</span>
                </div>
              </div>

              {/* Tax Buoyancy */}
              <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-semibold">Tax Buoyancy Factor</span>
                  <span className="font-mono font-bold text-emerald-400">{taxBuoyancy}x</span>
                </div>
                <input
                  type="range"
                  min="0.7"
                  max="1.6"
                  step="0.05"
                  value={taxBuoyancy}
                  onChange={(e) => setTaxBuoyancy(parseFloat(e.target.value))}
                  className="w-full accent-emerald-500 cursor-pointer"
                />
                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span>0.7x (Subdued)</span>
                  <span>1.1x (Base)</span>
                  <span>1.6x (Buoyant)</span>
                </div>
              </div>

            </div>

            {/* Simulation Results Display */}
            {simResults && (
              <div className="mt-4 p-5 rounded-xl bg-slate-950 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase tracking-wider font-bold text-slate-400">Simulated Econometric Projections</span>
                  <span className={`text-xs px-2.5 py-1 rounded-full font-bold ${
                    simResults.outputs.simulated_fiscal_deficit_pct_gdp <= 4.9
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {simResults.outputs.risk_level}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-xs text-slate-400">Simulated Fiscal Deficit</span>
                    <div className="text-2xl font-black text-white font-mono mt-1">
                      {simResults.outputs.simulated_fiscal_deficit_pct_gdp}%
                    </div>
                    <span className="text-[11px] text-slate-400 font-mono">
                      Baseline: 4.90% ({simResults.outputs.fiscal_variance_pct >= 0 ? '+' : ''}{simResults.outputs.fiscal_variance_pct}%)
                    </span>
                  </div>

                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-xs text-slate-400">Net Tax Inflows</span>
                    <div className="text-2xl font-black text-emerald-400 font-mono mt-1">
                      ₹{simResults.outputs.simulated_tax_receipts_cr.toLocaleString()} Cr
                    </div>
                    <span className="text-[11px] text-slate-400">Based on {taxBuoyancy}x buoyancy</span>
                  </div>

                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-xs text-slate-400">Total Outlay Required</span>
                    <div className="text-2xl font-black text-blue-400 font-mono mt-1">
                      ₹{simResults.outputs.simulated_total_outlay_cr.toLocaleString()} Cr
                    </div>
                    <span className="text-[11px] text-slate-400">Subsidies: ₹{simResults.outputs.simulated_subsidies_cr.toLocaleString()} Cr</span>
                  </div>

                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-xs text-slate-400">Simulated Nominal GDP</span>
                    <div className="text-2xl font-black text-purple-400 font-mono mt-1">
                      ₹{(simResults.outputs.simulated_nominal_gdp_cr / 100000).toFixed(1)}L Cr
                    </div>
                    <span className="text-[11px] text-slate-400">Base: ₹326 Lakh Crore</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-blue-950/20 border border-blue-900/30 text-xs text-slate-300 leading-relaxed">
                  <span className="font-bold text-blue-400">Economist Simulation Assessment: </span>
                  {simResults.outputs.risk_narrative}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 4. Subsidies & Rationalization */}
      {activeSubView === 'subsidies' && (
        <div className="space-y-6">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Wallet className="h-4 w-4 text-emerald-400" />
                Subsidies Trajectory &amp; Rationalization (Food, Fertilizer, Fuel)
              </h3>
              <p className="text-xs text-slate-400">
                Subsidies pruned from pandemic high of ₹7.07 Lakh Crore (3.57% GDP) to ₹3.81 Lakh Crore (1.17% GDP)
              </p>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={subsidiesChartData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                  <XAxis dataKey="year" stroke="#64748b" fontSize={11} angle={-20} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k Cr`} />
                  <Tooltip
                    formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')} Cr`]}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Bar dataKey="Food Subsidy" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Fertilizer Subsidy" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Petroleum Subsidy" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="overflow-x-auto no-scrollbar pt-2">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-800/70 text-slate-400 uppercase text-[10px]">
                  <tr>
                    <th className="p-2.5">Year</th>
                    <th className="p-2.5">Food (NFSA/PMGKAY)</th>
                    <th className="p-2.5">Fertilizer (Urea/NBS)</th>
                    <th className="p-2.5">Petroleum (LPG)</th>
                    <th className="p-2.5">Total Subsidies</th>
                    <th className="p-2.5">% of Union Budget</th>
                    <th className="p-2.5">% of GDP</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-200 font-mono">
                  {(overviewData?.subsidies || []).map((s: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-800/40">
                      <td className="p-2.5 font-bold text-white">{s.year}</td>
                      <td className="p-2.5">₹{s.food.toLocaleString()} Cr</td>
                      <td className="p-2.5">₹{s.fertilizer.toLocaleString()} Cr</td>
                      <td className="p-2.5">₹{s.petroleum.toLocaleString()} Cr</td>
                      <td className="p-2.5 font-bold text-emerald-400">₹{s.total.toLocaleString()} Cr</td>
                      <td className="p-2.5 text-blue-400">{s.pct_of_budget}%</td>
                      <td className="p-2.5 text-amber-400 font-semibold">{s.pct_of_gdp}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 5. 15th FC State Devolution */}
      {activeSubView === 'devolution' && (
        <div className="space-y-6">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Landmark className="h-4 w-4 text-blue-400" />
                  15th Finance Commission State Devolution Explorer (41% Divisible Pool)
                </h3>
                <p className="text-xs text-slate-400">
                  Total transfers of ₹9,64,102 Crore to Indian States under constitutional tax devolution formula.
                </p>
              </div>

              <input
                type="text"
                placeholder="Search state..."
                value={stateSearch}
                onChange={(e) => setStateSearch(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500 max-w-xs"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {filteredStates.map((st: any, i: number) => (
                <div key={i} className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-white truncate pr-2">{st.state}</span>
                    <span className="font-mono text-xs font-black text-blue-400">{st.share_pct}%</span>
                  </div>
                  <div className="text-sm font-mono font-bold text-emerald-400">
                    ₹{st.estimated_transfer_cr.toLocaleString()} Cr
                  </div>
                  <div className="w-full bg-slate-700 h-1 rounded-full overflow-hidden">
                    <div
                      className="bg-blue-500 h-full rounded-full"
                      style={{ width: `${(st.share_pct / 18.0) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 6. Tax Regime Comparison Calculator */}
      {activeSubView === 'tax_calc' && (
        <div className="space-y-6">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Calculator className="h-4 w-4 text-emerald-400" />
                Union Budget FY 2024-25 Income Tax Regime Comparison
              </h3>
              <p className="text-xs text-slate-400">
                New Tax Regime features enhanced ₹75,000 standard deduction and rationalized slabs up to ₹17,500 tax reduction.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Gross Annual Salary (₹)</label>
                <input
                  type="number"
                  value={grossIncome}
                  onChange={(e) => setGrossIncome(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Section 80C (PPF, ELSS, EPF)</label>
                <input
                  type="number"
                  value={sec80c}
                  onChange={(e) => setSec80c(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Section 80D (Health Insurance)</label>
                <input
                  type="number"
                  value={sec80d}
                  onChange={(e) => setSec80d(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">HRA Exemption Claim</label>
                <input
                  type="number"
                  value={hra}
                  onChange={(e) => setHra(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>
            </div>

            {taxCalcResult && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                
                {/* New Regime */}
                <div className={`p-4 rounded-xl border space-y-3 ${
                  taxCalcResult.recommended_regime === 'New Tax Regime'
                    ? 'bg-emerald-950/20 border-emerald-500/40 ring-1 ring-emerald-500/40'
                    : 'bg-slate-800/40 border-slate-700/60'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">New Tax Regime (Default)</span>
                    {taxCalcResult.recommended_regime === 'New Tax Regime' && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
                        RECOMMENDED
                      </span>
                    )}
                  </div>
                  <div className="space-y-1.5 text-xs text-slate-300">
                    <div className="flex justify-between"><span>Standard Deduction:</span><span className="font-mono">₹75,000</span></div>
                    <div className="flex justify-between"><span>Taxable Income:</span><span className="font-mono">₹{taxCalcResult.new_regime.taxable_income.toLocaleString()}</span></div>
                    <div className="flex justify-between"><span>Base Tax:</span><span className="font-mono">₹{taxCalcResult.new_regime.base_tax.toLocaleString()}</span></div>
                    <div className="flex justify-between"><span>4% Cess:</span><span className="font-mono">₹{taxCalcResult.new_regime.cess.toLocaleString()}</span></div>
                    <div className="flex justify-between pt-2 border-t border-slate-700/60 text-sm font-black text-emerald-400">
                      <span>Total Tax Liability:</span>
                      <span className="font-mono">₹{taxCalcResult.new_regime.total_tax.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Old Regime */}
                <div className={`p-4 rounded-xl border space-y-3 ${
                  taxCalcResult.recommended_regime === 'Old Tax Regime'
                    ? 'bg-blue-950/20 border-blue-500/40 ring-1 ring-blue-500/40'
                    : 'bg-slate-800/40 border-slate-700/60'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">Old Tax Regime</span>
                    {taxCalcResult.recommended_regime === 'Old Tax Regime' && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">
                        RECOMMENDED
                      </span>
                    )}
                  </div>
                  <div className="space-y-1.5 text-xs text-slate-300">
                    <div className="flex justify-between"><span>Standard Deduction:</span><span className="font-mono">₹50,000</span></div>
                    <div className="flex justify-between"><span>Total Deductions Claimed:</span><span className="font-mono">₹{taxCalcResult.old_regime.total_deductions_claimed.toLocaleString()}</span></div>
                    <div className="flex justify-between"><span>Taxable Income:</span><span className="font-mono">₹{taxCalcResult.old_regime.taxable_income.toLocaleString()}</span></div>
                    <div className="flex justify-between"><span>4% Cess:</span><span className="font-mono">₹{taxCalcResult.old_regime.cess.toLocaleString()}</span></div>
                    <div className="flex justify-between pt-2 border-t border-slate-700/60 text-sm font-black text-blue-400">
                      <span>Total Tax Liability:</span>
                      <span className="font-mono">₹{taxCalcResult.old_regime.total_tax.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

              </div>
            )}

            {taxCalcResult && (
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-amber-400 shrink-0" />
                <span className="text-xs text-slate-300">{taxCalcResult.explanation}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 7. UPSC & Constitutional Guide */}
      {activeSubView === 'upsc' && (
        <div className="space-y-6">
          
          {/* Constitutional Provisions */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-blue-400" />
              Constitutional Framework of Indian Budget (Articles 112 - 280)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {(upscData?.constitutional_provisions || []).map((cp: any, idx: number) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black text-blue-400">{cp.article}</span>
                    <span className="text-xs font-bold text-white">• {cp.title}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">{cp.details}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Deficit Taxonomy */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <h3 className="text-sm font-bold text-white">Types of Budgetary Deficits &amp; Policy Implications</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {(upscData?.deficit_taxonomy || []).map((dt: any, idx: number) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-1">
                  <span className="text-xs font-bold text-amber-400">{dt.name}</span>
                  <div className="text-xs font-mono text-slate-200 bg-slate-900/80 px-2 py-1 rounded">
                    {dt.formula}
                  </div>
                  <p className="text-[11px] text-slate-400">{dt.implication}</p>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
