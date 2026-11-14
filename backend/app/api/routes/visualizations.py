from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.budget import BudgetWorkspace, FinancialEntry
from app.schemas.budget import ChartDataRequest, ChartDataResponse

router = APIRouter()

@router.get("/chart-data/{workspace_id}/{chart_type}")
async def get_chart_data(
    workspace_id: str,
    chart_type: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetWorkspace).where(BudgetWorkspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    analysis = workspace.analysis_result or {}
    
    chart_data_map = {
        "receipt_composition": _get_receipt_composition,
        "expenditure_composition": _get_expenditure_composition,
        "revenue_vs_capital": _get_revenue_vs_capital,
        "fiscal_indicators": _get_fiscal_indicators,
        "sector_allocation": _get_sector_allocation,
        "top_ministries": _get_top_ministries,
        "tax_composition": _get_tax_composition,
        "deficit_trends": _get_deficit_trends,
        "scheme_comparison": _get_scheme_comparison,
        "budget_overview_kpi": _get_overview_kpi,
    }
    
    handler = chart_data_map.get(chart_type)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Unknown chart type: {chart_type}")
    
    return handler(analysis, workspace)

def _get_receipt_composition(analysis, workspace):
    receipts = analysis.get("receipts", {})
    data = receipts.get("receipt_composition", [])
    if not data:
        data = []
        if receipts.get("tax_revenue"):
            tax = receipts["tax_revenue"]
            if isinstance(tax, dict) and tax.get("total"):
                data.append({"name": "Tax Revenue", "value": tax["total"]})
        if receipts.get("non_tax_revenue"):
            ntax = receipts["non_tax_revenue"]
            if isinstance(ntax, dict) and ntax.get("total"):
                data.append({"name": "Non-Tax Revenue", "value": ntax["total"]})
        if receipts.get("capital_receipts"):
            data.append({"name": "Capital Receipts", "value": receipts["capital_receipts"]})
    return {"chart_type": "pie", "title": "Receipt Composition", "data": data, "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_expenditure_composition(analysis, workspace):
    exp = analysis.get("expenditure", {})
    data = exp.get("expenditure_composition", [])
    if not data:
        data = []
        if exp.get("revenue_expenditure"):
            data.append({"name": "Revenue Expenditure", "value": exp["revenue_expenditure"]})
        if exp.get("capital_expenditure"):
            data.append({"name": "Capital Expenditure", "value": exp["capital_expenditure"]})
    return {"chart_type": "pie", "title": "Expenditure Composition", "data": data, "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_revenue_vs_capital(analysis, workspace):
    receipts = analysis.get("receipts", {})
    exp = analysis.get("expenditure", {})
    data = [
        {"category": "Receipts", "Revenue": receipts.get("revenue_receipts", 0), "Capital": receipts.get("capital_receipts", 0)},
        {"category": "Expenditure", "Revenue": exp.get("revenue_expenditure", 0), "Capital": exp.get("capital_expenditure", 0)},
    ]
    return {"chart_type": "grouped_bar", "title": "Revenue vs Capital", "data": data, "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_fiscal_indicators(analysis, workspace):
    fiscal = analysis.get("fiscal", {})
    indicators = fiscal.get("fiscal_indicators", [])
    return {"chart_type": "kpi_cards", "title": "Fiscal Indicators", "data": indicators, "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_sector_allocation(analysis, workspace):
    sectors = analysis.get("sectors", {})
    data = sectors.get("sectors", [])
    return {"chart_type": "treemap", "title": "Sector-wise Allocation", "data": data, "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_top_ministries(analysis, workspace):
    exp = analysis.get("expenditure", {})
    data = exp.get("top_spending_ministries", exp.get("ministry_wise", []))
    return {"chart_type": "horizontal_bar", "title": "Top Spending Ministries", "data": data[:15] if data else [], "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_tax_composition(analysis, workspace):
    receipts = analysis.get("receipts", {})
    tax = receipts.get("tax_revenue", {})
    data = []
    if isinstance(tax, dict):
        for k, v in tax.items():
            if k not in ("total", "analysis", "yoy_change") and isinstance(v, (int, float)):
                name = k.replace("_", " ").title()
                data.append({"name": name, "value": v})
    return {"chart_type": "doughnut", "title": "Tax Revenue Composition", "data": data, "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_deficit_trends(analysis, workspace):
    fiscal = analysis.get("fiscal", {})
    data = fiscal.get("historical_trends", [])
    return {"chart_type": "line", "title": "Deficit Trends", "data": data, "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_scheme_comparison(analysis, workspace):
    schemes = analysis.get("schemes", {})
    data = schemes.get("schemes", [])[:20]
    return {"chart_type": "bar", "title": "Top Scheme Allocations", "data": data, "units": "₹ Crore", "financial_year": workspace.financial_year}

def _get_overview_kpi(analysis, workspace):
    overview = analysis.get("overview", {})
    data = [
        {"label": "Total Receipts", "value": overview.get("total_receipts"), "unit": "₹ Cr"},
        {"label": "Total Expenditure", "value": overview.get("total_expenditure"), "unit": "₹ Cr"},
        {"label": "Fiscal Deficit", "value": overview.get("fiscal_deficit"), "unit": "₹ Cr"},
        {"label": "Revenue Deficit", "value": overview.get("revenue_deficit"), "unit": "₹ Cr"},
        {"label": "Capital Expenditure", "value": overview.get("capital_expenditure"), "unit": "₹ Cr"},
        {"label": "Revenue Expenditure", "value": overview.get("revenue_expenditure"), "unit": "₹ Cr"},
    ]
    return {"chart_type": "kpi_cards", "title": "Budget Overview", "data": [d for d in data if d["value"] is not None], "units": "₹ Crore", "financial_year": workspace.financial_year}
