from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.services.union_intelligence.intelligence_service import UnionBudgetIntelligenceService

router = APIRouter()

class WhatIfSimulationRequest(BaseModel):
    nominal_gdp_growth_pct: float = Field(default=10.5, ge=2.0, le=25.0)
    crude_oil_price_usd: float = Field(default=80.0, ge=40.0, le=160.0)
    disinvestment_realization_pct: float = Field(default=100.0, ge=0.0, le=200.0)
    tax_buoyancy: float = Field(default=1.1, ge=0.5, le=2.5)

class TaxCalculationRequest(BaseModel):
    gross_annual_income: float = Field(..., ge=0.0)
    sec_80c_investment: float = Field(default=150000.0, ge=0.0)
    sec_80d_health: float = Field(default=25000.0, ge=0.0)
    hra_exemption: float = Field(default=0.0, ge=0.0)
    other_deductions: float = Field(default=0.0, ge=0.0)

@router.get("/overview")
async def get_union_intelligence_overview():
    """Returns complete Union Budget analytical series, Sankey flows, and 10-year trends."""
    return UnionBudgetIntelligenceService.get_comprehensive_overview()

@router.post("/simulate")
async def run_what_if_simulation(req: WhatIfSimulationRequest):
    """Executes What-If economic policy simulation and sensitivity models."""
    return UnionBudgetIntelligenceService.simulate_economic_scenario(
        nominal_gdp_growth_pct=req.nominal_gdp_growth_pct,
        crude_oil_price_usd=req.crude_oil_price_usd,
        disinvestment_realization_pct=req.disinvestment_realization_pct,
        tax_buoyancy=req.tax_buoyancy,
    )

@router.post("/calculate-tax")
async def calculate_tax_regimes(req: TaxCalculationRequest):
    """Compares Old vs New Tax Regime with FY 2024-25 standard deduction and updated slabs."""
    return UnionBudgetIntelligenceService.calculate_tax_regimes(
        gross_annual_income=req.gross_annual_income,
        sec_80c_investment=req.sec_80c_investment,
        sec_80d_health=req.sec_80d_health,
        hra_exemption=req.hra_exemption,
        other_deductions=req.other_deductions,
    )

@router.get("/upsc-insights")
async def get_upsc_and_policy_insights():
    """Constitutional provisions, FRBM Act benchmarks, and economic terminology dictionary."""
    return UnionBudgetIntelligenceService.get_upsc_and_constitutional_framework()
