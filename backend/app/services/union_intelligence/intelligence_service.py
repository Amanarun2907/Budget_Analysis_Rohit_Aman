from typing import Dict, Any, List, Optional
import math

class UnionBudgetIntelligenceService:
    """
    Comprehensive Indian Union Budget Intelligence & Analytical Engine.
    Covers multi-year historical series (BE vs RE vs Actuals), Sankey flows,
    tax regime analytics, What-If simulation engine, and federal devolution models.
    """

    # 10-Year Historical Official Series (FY 2014-15 to FY 2024-25)
    # Sourced from Union Budget Documents, Economic Surveys, & CGA Actuals.
    HISTORICAL_SERIES = [
        {"year": "2014-15", "be_exp": 1794892, "re_exp": 1681158, "actual_exp": 1663673, "capex": 196607, "rev_exp": 1467066, "rev_rec": 1101472, "fiscal_def_pct": 4.1, "nominal_gdp": 12467959},
        {"year": "2015-16", "be_exp": 1777477, "re_exp": 1785391, "actual_exp": 1790783, "capex": 235253, "rev_exp": 1555530, "rev_rec": 1195025, "fiscal_def_pct": 3.9, "nominal_gdp": 13771874},
        {"year": "2016-17", "be_exp": 1978060, "re_exp": 2014407, "actual_exp": 1975194, "capex": 284347, "rev_exp": 1690847, "rev_rec": 1374203, "fiscal_def_pct": 3.5, "nominal_gdp": 15391669},
        {"year": "2017-18", "be_exp": 2146735, "re_exp": 2217750, "actual_exp": 2141973, "capex": 263140, "rev_exp": 1878833, "rev_rec": 1435232, "fiscal_def_pct": 3.5, "nominal_gdp": 17095005},
        {"year": "2018-19", "be_exp": 2442213, "re_exp": 2457235, "actual_exp": 2315113, "capex": 303884, "rev_exp": 2011229, "rev_rec": 1552916, "fiscal_def_pct": 3.4, "nominal_gdp": 18886957},
        {"year": "2019-20", "be_exp": 2786349, "re_exp": 2698552, "actual_exp": 2686330, "capex": 335726, "rev_exp": 2350604, "rev_rec": 1684059, "fiscal_def_pct": 4.6, "nominal_gdp": 20074856},
        {"year": "2020-21", "be_exp": 3042230, "re_exp": 3450305, "actual_exp": 3509836, "capex": 426309, "rev_exp": 3083527, "rev_rec": 1633919, "fiscal_def_pct": 9.2, "nominal_gdp": 19829938},
        {"year": "2021-22", "be_exp": 3483236, "re_exp": 3770000, "actual_exp": 3793734, "capex": 592874, "rev_exp": 3200860, "rev_rec": 2169905, "fiscal_def_pct": 6.7, "nominal_gdp": 23471012},
        {"year": "2022-23", "be_exp": 3944909, "re_exp": 4187228, "actual_exp": 4193157, "capex": 736340, "rev_exp": 3456817, "rev_rec": 2383206, "fiscal_def_pct": 6.4, "nominal_gdp": 26950360},
        {"year": "2023-24", "be_exp": 4503097, "re_exp": 4490486, "actual_exp": 4442542, "capex": 948506, "rev_exp": 3494036, "rev_rec": 2728286, "fiscal_def_pct": 5.6, "nominal_gdp": 29658097},
        {"year": "2024-25", "be_exp": 4820512, "re_exp": 4820512, "actual_exp": None, "capex": 1111111, "rev_exp": 3709401, "rev_rec": 3129250, "fiscal_def_pct": 4.9, "nominal_gdp": 32600000},
    ]

    # Rupee Flows (Where Rupee Comes From & Where Rupee Goes To)
    RUPEE_FLOWS = {
        "comes_from": [
            {"source": "Borrowings and Other Liabilities", "share_paise": 27, "amount_cr": 1301538, "category": "Debt Capital Receipts"},
            {"source": "Income Tax (Personal)", "share_paise": 19, "amount_cr": 915897, "category": "Direct Taxes"},
            {"source": "Goods and Services Tax (GST)", "share_paise": 18, "amount_cr": 867692, "category": "Indirect Taxes"},
            {"source": "Corporation Tax", "share_paise": 17, "amount_cr": 819487, "category": "Direct Taxes"},
            {"source": "Non-Tax Receipts (Dividends/Surplus)", "share_paise": 9, "amount_cr": 433846, "category": "Non-Tax Revenues"},
            {"source": "Union Excise Duties", "share_paise": 5, "amount_cr": 241026, "category": "Indirect Taxes"},
            {"source": "Customs Duties", "share_paise": 4, "amount_cr": 192820, "category": "Indirect Taxes"},
            {"source": "Non-Debt Capital Receipts (Recoveries)", "share_paise": 1, "amount_cr": 48205, "category": "Non-Debt Capital"}
        ],
        "goes_to": [
            {"destination": "States' Share of Taxes & Duties", "share_paise": 20, "amount_cr": 964102, "category": "Federal Transfers"},
            {"destination": "Interest Payments", "share_paise": 20, "amount_cr": 964102, "category": "Committed Expenditure"},
            {"destination": "Central Sector Schemes", "share_paise": 16, "amount_cr": 771282, "category": "Union Development"},
            {"destination": "Centrally Sponsored Schemes", "share_paise": 8, "amount_cr": 385641, "category": "State Linkage Schemes"},
            {"destination": "Finance Commission & Other Transfers", "share_paise": 8, "amount_cr": 385641, "category": "Federal Transfers"},
            {"destination": "Defence Allocations", "share_paise": 8, "amount_cr": 385641, "category": "National Security"},
            {"destination": "Subsidies (Food, Fertilizer, Fuel)", "share_paise": 6, "amount_cr": 289231, "category": "Welfare Transfers"},
            {"destination": "Pensions Outgo", "share_paise": 4, "amount_cr": 192820, "category": "Committed Expenditure"},
            {"destination": "Other Expenditure & Capital Outlay", "share_paise": 8, "amount_cr": 385641, "category": "Capital & Administrative"}
        ]
    }

    # 15th Finance Commission State Devolution Share Matrix (41% divisible pool)
    STATE_DEVOLUTION_SHARES = [
        {"state": "Uttar Pradesh", "share_pct": 17.939, "estimated_transfer_cr": 172950},
        {"state": "Bihar", "share_pct": 10.058, "estimated_transfer_cr": 96976},
        {"state": "Madhya Pradesh", "share_pct": 7.850, "estimated_transfer_cr": 75682},
        {"state": "West Bengal", "share_pct": 7.523, "estimated_transfer_cr": 72530},
        {"state": "Maharashtra", "share_pct": 6.317, "estimated_transfer_cr": 60902},
        {"state": "Rajasthan", "share_pct": 6.026, "estimated_transfer_cr": 58097},
        {"state": "Odisha", "share_pct": 4.528, "estimated_transfer_cr": 43655},
        {"state": "Tamil Nadu", "share_pct": 4.079, "estimated_transfer_cr": 39326},
        {"state": "Andhra Pradesh", "share_pct": 4.047, "estimated_transfer_cr": 39017},
        {"state": "Karnataka", "share_pct": 3.647, "estimated_transfer_cr": 35161},
        {"state": "Gujarat", "share_pct": 3.478, "estimated_transfer_cr": 33532},
        {"state": "Jharkhand", "share_pct": 3.307, "estimated_transfer_cr": 31883},
        {"state": "Kerala", "share_pct": 1.925, "estimated_transfer_cr": 18559},
        {"state": "Telangana", "share_pct": 2.102, "estimated_transfer_cr": 20265},
        {"state": "Punjab", "share_pct": 1.807, "estimated_transfer_cr": 17421},
        {"state": "Assam", "share_pct": 3.128, "estimated_transfer_cr": 30157},
        {"state": "Other States & UTs", "share_pct": 12.199, "estimated_transfer_cr": 117589}
    ]

    # Major Subsidies Overview (₹ Crore)
    SUBSIDIES_SERIES = [
        {"year": "2020-21", "food": 541330, "fertilizer": 127922, "petroleum": 38166, "total": 707418, "pct_of_budget": 20.2, "pct_of_gdp": 3.57},
        {"year": "2021-22", "food": 288969, "fertilizer": 153758, "petroleum": 3921, "total": 446648, "pct_of_budget": 11.8, "pct_of_gdp": 1.90},
        {"year": "2022-23", "food": 272802, "fertilizer": 251339, "petroleum": 6817, "total": 530958, "pct_of_budget": 12.7, "pct_of_gdp": 1.97},
        {"year": "2023-24 (RE)", "food": 212394, "fertilizer": 188894, "petroleum": 12240, "total": 413528, "pct_of_budget": 9.2, "pct_of_gdp": 1.39},
        {"year": "2024-25 (BE)", "food": 205250, "fertilizer": 164000, "petroleum": 11925, "total": 381175, "pct_of_budget": 7.9, "pct_of_gdp": 1.17}
    ]

    @classmethod
    def get_comprehensive_overview(cls) -> Dict[str, Any]:
        """Provides rich historical, flow, and analytical summary."""
        # Calculate 10-year Capex CAGR
        c0 = cls.HISTORICAL_SERIES[0]["capex"]
        c1 = cls.HISTORICAL_SERIES[-1]["capex"]
        n_years = len(cls.HISTORICAL_SERIES) - 1
        capex_cagr = round(((c1 / c0) ** (1.0 / n_years) - 1.0) * 100, 2)

        # Calculate Total Outlay CAGR
        t0 = cls.HISTORICAL_SERIES[0]["be_exp"]
        t1 = cls.HISTORICAL_SERIES[-1]["be_exp"]
        outlay_cagr = round(((t1 / t0) ** (1.0 / n_years) - 1.0) * 100, 2)

        return {
            "historical_series": cls.HISTORICAL_SERIES,
            "rupee_flows": cls.RUPEE_FLOWS,
            "state_devolution": cls.STATE_DEVOLUTION_SHARES,
            "subsidies": cls.SUBSIDIES_SERIES,
            "kpis": {
                "total_budget_be_fy25": 4820512,
                "capex_be_fy25": 1111111,
                "capex_to_total_ratio": 23.05,
                "capex_10yr_cagr": capex_cagr,
                "outlay_10yr_cagr": outlay_cagr,
                "fiscal_deficit_target_fy25": 4.9,
                "fiscal_deficit_glide_path_fy26": "<4.5%",
                "states_devolution_pool_cr": 964102,
                "total_subsidies_cr": 381175,
                "subsidies_pct_gdp": 1.17,
            }
        }

    @classmethod
    def simulate_economic_scenario(
        cls,
        nominal_gdp_growth_pct: float = 10.5,
        crude_oil_price_usd: float = 80.0,
        disinvestment_realization_pct: float = 100.0,
        tax_buoyancy: float = 1.1,
    ) -> Dict[str, Any]:
        """
        Interactive What-If Economic Policy Simulator.
        Mathematically projects Fiscal Deficit, Revenue, and Outlay impacts.
        """
        base_gdp = 32600000.0  # ₹326 Lakh Cr for FY25
        base_tax_rec = 2583499.0
        base_non_tax = 545751.0
        base_disinvest = 50000.0
        base_exp = 4820512.0
        base_subsidies = 381175.0

        # 1. GDP sensitivity
        gdp_factor = (nominal_gdp_growth_pct - 10.5) / 100.0
        sim_gdp = base_gdp * (1.0 + gdp_factor)

        # 2. Tax Revenue = Base + Buoyancy * Growth Delta
        sim_tax_revenue = base_tax_rec * (1.0 + (gdp_factor * tax_buoyancy))

        # 3. Oil Sensitivity ($10 hike in crude increases fertilizer/LPG subsidies by ~₹18,000 Cr)
        oil_delta = crude_oil_price_usd - 80.0
        subsidy_impact = (oil_delta / 10.0) * 18000.0 if oil_delta > 0 else (oil_delta / 10.0) * 12000.0
        sim_subsidies = max(200000.0, base_subsidies + subsidy_impact)
        sim_exp = base_exp + (sim_subsidies - base_subsidies)

        # 4. Disinvestment Realization
        sim_disinvest = base_disinvest * (disinvestment_realization_pct / 100.0)
        disinvest_impact = sim_disinvest - base_disinvest

        # Total Non-Debt Receipts
        sim_non_debt_receipts = sim_tax_revenue + base_non_tax + (base_disinvest + disinvest_impact) + 27950.0

        # Simulated Fiscal Deficit
        sim_fiscal_def = sim_exp - sim_non_debt_receipts
        sim_fiscal_def_pct = round((sim_fiscal_def / sim_gdp) * 100.0, 2)

        # Risk assessment text
        if sim_fiscal_def_pct <= 4.7:
            risk_level = "Low Fiscal Risk / Over-achievement"
            narrative = "Strong tax buoyancy and moderate global crude yield an accelerated consolidation path below the FRBM target."
        elif sim_fiscal_def_pct <= 5.1:
            risk_level = "Baseline Compliance"
            narrative = "Macroeconomic projections stay within the targeted 4.9% (+/- 0.2%) corridor, maintaining macroeconomic stability."
        else:
            risk_level = "Elevated Fiscal Pressure"
            narrative = "Higher energy subsidies and lower tax buoyancy increase market borrowing requirements, exerting upward pressure on 10-year G-Sec yields."

        return {
            "inputs": {
                "nominal_gdp_growth_pct": nominal_gdp_growth_pct,
                "crude_oil_price_usd": crude_oil_price_usd,
                "disinvestment_realization_pct": disinvestment_realization_pct,
                "tax_buoyancy": tax_buoyancy,
            },
            "outputs": {
                "simulated_nominal_gdp_cr": round(sim_gdp, 2),
                "simulated_tax_receipts_cr": round(sim_tax_revenue, 2),
                "simulated_total_outlay_cr": round(sim_exp, 2),
                "simulated_subsidies_cr": round(sim_subsidies, 2),
                "simulated_fiscal_deficit_cr": round(sim_fiscal_def, 2),
                "simulated_fiscal_deficit_pct_gdp": sim_fiscal_def_pct,
                "baseline_fiscal_deficit_pct_gdp": 4.9,
                "fiscal_variance_pct": round(sim_fiscal_def_pct - 4.9, 2),
                "risk_level": risk_level,
                "risk_narrative": narrative,
            }
        }

    @classmethod
    def calculate_tax_regimes(
        cls,
        gross_annual_income: float,
        sec_80c_investment: float = 150000.0,
        sec_80d_health: float = 25000.0,
        hra_exemption: float = 0.0,
        other_deductions: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculates exact tax liability comparing Old Regime vs New Regime (Budget FY25).
        New Regime incorporates ₹75,000 standard deduction and updated tax slabs.
        """
        # 1. New Tax Regime (FY 2024-25)
        new_std_deduction = 75000.0
        taxable_income_new = max(0.0, gross_annual_income - new_std_deduction)

        # New Slabs:
        # 0 - 3L: Nil
        # 3L - 7L: 5%
        # 7L - 10L: 10%
        # 10L - 12L: 15%
        # 12L - 15L: 20%
        # > 15L: 30%
        tax_new = 0.0
        if taxable_income_new > 1500000:
            tax_new += (taxable_income_new - 1500000) * 0.30
            tax_new += 300000 * 0.20
            tax_new += 200000 * 0.15
            tax_new += 300000 * 0.10
            tax_new += 400000 * 0.05
        elif taxable_income_new > 1200000:
            tax_new += (taxable_income_new - 1200000) * 0.20
            tax_new += 200000 * 0.15
            tax_new += 300000 * 0.10
            tax_new += 400000 * 0.05
        elif taxable_income_new > 1000000:
            tax_new += (taxable_income_new - 1000000) * 0.15
            tax_new += 300000 * 0.10
            tax_new += 400000 * 0.05
        elif taxable_income_new > 700000:
            tax_new += (taxable_income_new - 700000) * 0.10
            tax_new += 400000 * 0.05
        elif taxable_income_new > 300000:
            tax_new += (taxable_income_new - 300000) * 0.05

        # Section 87A rebate in New Regime: Taxable income up to ₹7,00,000 pays 0 tax
        if taxable_income_new <= 700000:
            tax_new = 0.0

        # 4% Health & Education Cess
        cess_new = tax_new * 0.04
        total_tax_new = round(tax_new + cess_new, 2)

        # 2. Old Tax Regime
        old_std_deduction = 50000.0
        total_old_deductions = old_std_deduction + min(150000.0, sec_80c_investment) + min(100000.0, sec_80d_health) + hra_exemption + other_deductions
        taxable_income_old = max(0.0, gross_annual_income - total_old_deductions)

        # Old Slabs:
        # 0 - 2.5L: Nil
        # 2.5L - 5L: 5%
        # 5L - 10L: 20%
        # > 10L: 30%
        tax_old = 0.0
        if taxable_income_old > 1000000:
            tax_old += (taxable_income_old - 1000000) * 0.30
            tax_old += 500000 * 0.20
            tax_old += 250000 * 0.05
        elif taxable_income_old > 500000:
            tax_old += (taxable_income_old - 500000) * 0.20
            tax_old += 250000 * 0.05
        elif taxable_income_old > 250000:
            tax_old += (taxable_income_old - 250000) * 0.05

        # Section 87A rebate in Old Regime: Taxable income up to ₹5,00,000 pays 0 tax
        if taxable_income_old <= 500000:
            tax_old = 0.0

        cess_old = tax_old * 0.04
        total_tax_old = round(tax_old + cess_old, 2)

        # Recommendation
        diff = round(abs(total_tax_new - total_tax_old), 2)
        if total_tax_new < total_tax_old:
            rec = "New Tax Regime"
            savings = diff
            reason = f"You save ₹{savings:,.0f} annually under the New Tax Regime due to lower slab rates and enhanced ₹75,000 standard deduction."
        elif total_tax_old < total_tax_new:
            rec = "Old Tax Regime"
            savings = diff
            reason = f"You save ₹{savings:,.0f} annually under the Old Tax Regime by claiming ₹{total_old_deductions:,.0f} in Chapter VI-A deductions (80C, 80D, HRA)."
        else:
            rec = "Both Regimes Equal"
            savings = 0.0
            reason = "Both tax regimes yield the exact same tax liability."

        return {
            "gross_income": gross_annual_income,
            "new_regime": {
                "standard_deduction": new_std_deduction,
                "taxable_income": taxable_income_new,
                "base_tax": round(tax_new, 2),
                "cess": round(cess_new, 2),
                "total_tax": total_tax_new,
                "effective_tax_rate_pct": round((total_tax_new / max(gross_annual_income, 1)) * 100, 2),
            },
            "old_regime": {
                "standard_deduction": old_std_deduction,
                "total_deductions_claimed": round(total_old_deductions, 2),
                "taxable_income": taxable_income_old,
                "base_tax": round(tax_old, 2),
                "cess": round(cess_old, 2),
                "total_tax": total_tax_old,
                "effective_tax_rate_pct": round((total_tax_old / max(gross_annual_income, 1)) * 100, 2),
            },
            "recommended_regime": rec,
            "annual_savings": savings,
            "explanation": reason,
        }

    @classmethod
    def get_upsc_and_constitutional_framework(cls) -> Dict[str, Any]:
        """Provides constitutional articles, statutory guidelines, and core concepts."""
        return {
            "constitutional_provisions": [
                {
                    "article": "Article 112",
                    "title": "Annual Financial Statement (AFS)",
                    "details": "The President causes to be laid before both Houses of Parliament a statement of estimated receipts and expenditure of the Government of India for the financial year. The word 'Budget' is not used in the Constitution."
                },
                {
                    "article": "Article 113",
                    "title": "Demands for Grants & Voting Procedure",
                    "details": "Estimates relating to expenditure charged upon the Consolidated Fund of India are not submitted to the vote of Parliament, but can be discussed. Other expenditure is submitted as Demands for Grants to the Lok Sabha."
                },
                {
                    "article": "Article 114",
                    "title": "Appropriation Bill",
                    "details": "No money can be withdrawn from the Consolidated Fund of India except under appropriation made by law passed by Parliament."
                },
                {
                    "article": "Article 110",
                    "title": "Money Bills",
                    "details": "Defines what constitutes a Money Bill (imposition, abolition, remission, alteration or regulation of any tax; regulation of borrowing; custody of Consolidated Fund). Certified solely by the Speaker of the Lok Sabha."
                },
                {
                    "article": "Article 266(1)",
                    "title": "Consolidated Fund of India",
                    "details": "All revenues received by the Government, loans raised, and monies received in repayment of loans form one consolidated fund. No money can be spent without Parliamentary authorization."
                },
                {
                    "article": "Article 267",
                    "title": "Contingency Fund of India",
                    "details": "An imprest fund placed at the disposal of the President to enable advances to be made for unforeseen expenditure, pending authorization by Parliament (corpus expanded to ₹30,000 Cr)."
                },
                {
                    "article": "Article 280",
                    "title": "Finance Commission",
                    "details": "Constitutional body constituted every 5 years by the President to recommend the distribution of net tax proceeds between the Union and States, and allocation among States."
                }
            ],
            "frbm_statutory_mandate": {
                "act": "Fiscal Responsibility and Budget Management (FRBM) Act, 2003",
                "key_objectives": [
                    "Institutionalize financial discipline to reduce fiscal deficit.",
                    "Ensure inter-generational equity in fiscal management.",
                    "Mandate presentation of Macroeconomic Framework Statement, Medium-Term Fiscal Policy Statement, and Fiscal Policy Strategy Statement."
                ],
                "statutory_targets": "Central government debt target of 40% of GDP; General government debt target of 60% of GDP; Fiscal deficit glide path targeting <4.5% by FY 2025-26.",
                "escape_clause": "Section 4(2) permits deviation from fiscal deficit target on grounds of national security, acts of war, national calamity, collapse of agriculture, structural reforms, or severe decline in real output growth."
            },
            "deficit_taxonomy": [
                {
                    "name": "Gross Fiscal Deficit",
                    "formula": "Total Expenditure - (Revenue Receipts + Non-Debt Capital Receipts)",
                    "implication": "Measures total net borrowing requirement of the government from all sources."
                },
                {
                    "name": "Revenue Deficit",
                    "formula": "Revenue Expenditure - Revenue Receipts",
                    "implication": "Reflects borrowing used for recurring consumption (government dissaving) rather than productive asset creation."
                },
                {
                    "name": "Effective Revenue Deficit",
                    "formula": "Revenue Deficit - Grants for Creation of Capital Assets",
                    "implication": "Excludes capital asset grants given to States, showing true structural government consumption."
                },
                {
                    "name": "Primary Deficit",
                    "formula": "Gross Fiscal Deficit - Interest Payments",
                    "implication": "Reflects the fiscal stance of the current government independent of past debt liabilities inherited."
                }
            ]
        }
