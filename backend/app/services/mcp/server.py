from typing import Dict, Any, List, Optional
import structlog
from app.services.union_intelligence.intelligence_service import UnionBudgetIntelligenceService
from app.services.observability.tracker import observability_tracker

logger = structlog.get_logger()

class BudgetMCPServer:
    """
    Model Context Protocol (MCP) server for Union and State Budget Intelligence.
    Exposes standardized agent tools for external LLMs, IDE extensions, and automation pipelines.
    """

    TOOLS = [
        {
            "name": "get_union_budget_summary",
            "description": "Retrieve comprehensive macroeconomic summary of India's Union Budget FY25 (Total Outlay, Capex, Fiscal Deficit, Receipts)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "year": {"type": "string", "description": "Financial year, e.g. 2024-25"}
                }
            }
        },
        {
            "name": "get_historical_fiscal_series",
            "description": "Retrieve 10-year official series (FY15 to FY25) comparing BE vs RE vs Actuals, Capex CAGR, and Deficit ratios",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "enum": ["all", "capex", "fiscal_deficit", "be_vs_actuals"]}
                }
            }
        },
        {
            "name": "simulate_economic_scenario",
            "description": "Simulate what-if macroeconomic impact of GDP growth, crude oil price, disinvestment, and tax buoyancy on India's Fiscal Deficit",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "nominal_gdp_growth_pct": {"type": "number", "description": "Nominal GDP growth percentage (e.g. 10.5)"},
                    "crude_oil_price_usd": {"type": "number", "description": "Brent crude price in USD/barrel (e.g. 85.0)"},
                    "disinvestment_realization_pct": {"type": "number", "description": "Target realization percentage (e.g. 80.0)"},
                    "tax_buoyancy": {"type": "number", "description": "Tax buoyancy coefficient (e.g. 1.15)"}
                }
            }
        },
        {
            "name": "calculate_tax_comparison",
            "description": "Calculate exact personal income tax liabilities comparing New vs Old Tax Regime under FY 2024-25 slabs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "gross_annual_income": {"type": "number", "description": "Gross annual income in INR"},
                    "sec_80c_investment": {"type": "number", "description": "80C deductions (max 1,50,000)"},
                    "sec_80d_health": {"type": "number", "description": "Health insurance premium deduction"},
                    "hra_exemption": {"type": "number", "description": "House Rent Allowance exemption"}
                },
                "required": ["gross_annual_income"]
            }
        },
        {
            "name": "get_state_devolution_matrix",
            "description": "Retrieve 15th Finance Commission tax devolution shares (41% pool) for Indian States & UTs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "state_name": {"type": "string", "description": "Optional name of state, or omit for all"}
                }
            }
        },
        {
            "name": "verify_accounting_provenance",
            "description": "Audit and verify mathematical identities and Langfuse-style provenance traces for a budget workspace",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "description": "Workspace identifier"}
                }
            }
        }
    ]

    @classmethod
    def list_tools(cls) -> List[Dict[str, Any]]:
        return cls.TOOLS

    @classmethod
    def call_tool(cls, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Executing MCP Tool", tool_name=name, args=arguments)

        if name == "get_union_budget_summary":
            return UnionBudgetIntelligenceService.get_comprehensive_overview()["kpis"]

        elif name == "get_historical_fiscal_series":
            series = UnionBudgetIntelligenceService.HISTORICAL_SERIES
            metric = arguments.get("metric", "all")
            if metric == "capex":
                return [{"year": s["year"], "capex": s["capex"]} for s in series]
            elif metric == "fiscal_deficit":
                return [{"year": s["year"], "fiscal_deficit_pct": s["fiscal_def_pct"]} for s in series]
            elif metric == "be_vs_actuals":
                return [{"year": s["year"], "be": s["be_exp"], "re": s["re_exp"], "actual": s["actual_exp"]} for s in series]
            return series

        elif name == "simulate_economic_scenario":
            return UnionBudgetIntelligenceService.simulate_economic_scenario(
                nominal_gdp_growth_pct=arguments.get("nominal_gdp_growth_pct", 10.5),
                crude_oil_price_usd=arguments.get("crude_oil_price_usd", 80.0),
                disinvestment_realization_pct=arguments.get("disinvestment_realization_pct", 100.0),
                tax_buoyancy=arguments.get("tax_buoyancy", 1.1),
            )

        elif name == "calculate_tax_comparison":
            return UnionBudgetIntelligenceService.calculate_tax_regimes(
                gross_annual_income=arguments.get("gross_annual_income", 1200000.0),
                sec_80c_investment=arguments.get("sec_80c_investment", 150000.0),
                sec_80d_health=arguments.get("sec_80d_health", 25000.0),
                hra_exemption=arguments.get("hra_exemption", 0.0),
            )

        elif name == "get_state_devolution_matrix":
            st_name = arguments.get("state_name")
            shares = UnionBudgetIntelligenceService.STATE_DEVOLUTION_SHARES
            if st_name:
                filtered = [s for s in shares if st_name.lower() in s["state"].lower()]
                return filtered if filtered else shares
            return shares

        elif name == "verify_accounting_provenance":
            ws_id = arguments.get("workspace_id", "demo-workspace")
            return observability_tracker.get_latest_trace_for_workspace(ws_id)

        else:
            raise ValueError(f"Unknown tool: {name}")

mcp_server = BudgetMCPServer()
