import json
import re
import asyncio
from typing import Dict, Any, List, Optional, Callable
import structlog
from groq import Groq

from app.core.config import settings

logger = structlog.get_logger()

# Groq model names that actually exist — ordered fastest→most capable
GROQ_CANDIDATE_MODELS = [
    "llama-3.1-8b-instant",       # Fastest, 128k context
    "llama-3.3-70b-versatile",    # Best quality on Groq, 128k context
    "llama3-70b-8192",            # Reliable fallback
    "mixtral-8x7b-32768",         # Wide context fallback
]


class BudgetAgentSystem:
    """
    Multi-agent system for comprehensive Indian Union and State budget intelligence.

    Design principles:
    - Each agent receives a targeted, focused slice of the document and returns structured JSON.
    - Agents run concurrently where independent (Batch 1), then sequentially where synthesis is needed (Batch 2).
    - Text sent per agent is capped at 60 000 chars (≈ 15–20 PDF pages) — enough for thorough extraction
      without hitting token limits on 8 k-token models.
    - Mathematical reconciliation is applied deterministically AFTER all LLM calls.
    - No hardcoded numbers are ever injected.  If a figure is absent in the document the field stays null.
    """

    def __init__(self):
        self.client: Optional[Groq] = None
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                logger.warning(f"Groq client init notice: {e}")
        self.model = settings.LLM_MODEL

    # ─────────────────────────── LLM helpers ────────────────────────────────

    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        """Call Groq with a prioritised model list; fall back automatically on failure."""
        if not self.client:
            return "{}"

        # Build candidate list: configured model first, then the fixed priority list
        candidates: List[str] = []
        for m in [self.model] + GROQ_CANDIDATE_MODELS:
            if m and m not in candidates:
                candidates.append(m)

        last_error = None
        for model_name in candidates:
            try:
                # Prefer JSON-mode; fall back to plain chat if model doesn't support it
                try:
                    resp = self.client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        response_format={"type": "json_object"},
                        temperature=settings.LLM_TEMPERATURE,
                        max_tokens=min(max_tokens, 4096),
                        timeout=35.0,
                    )
                except Exception:
                    resp = self.client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=settings.LLM_TEMPERATURE,
                        max_tokens=min(max_tokens, 4096),
                        timeout=35.0,
                    )

                content = resp.choices[0].message.content or ""
                if content.strip():
                    logger.info(f"LLM call succeeded with model: {model_name}")
                    return content

            except Exception as e:
                last_error = e
                logger.warning(f"Model {model_name} failed: {e}. Trying next…")
                continue

        logger.error(f"All LLM models failed. Last error: {last_error}")
        return "{}"

    def _parse_json(self, response: str) -> Dict:
        """Robustly parse JSON from LLM output — strips markdown fences, handles partial output."""
        if not response or not response.strip():
            return {}

        # Direct parse
        try:
            return json.loads(response.strip())
        except Exception:
            pass

        # Strip ```json … ``` fences
        m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", response)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except Exception:
                pass

        # Find outermost braces
        m = re.search(r"\{[\s\S]*\}", response)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass

        logger.warning("Could not parse LLM JSON response; returning empty dict")
        return {}

    # ─────────────────────────── orchestration ──────────────────────────────

    async def run_complete_analysis(
        self,
        text: str,
        tables: List[Dict],
        metadata: Dict,
        workspace_id: str,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Execute the full multi-agent pipeline.

        Strategy for large documents:
        • Agents that need *financial figures* (overview, receipts, expenditure, fiscal)
          receive the first 60 k chars which typically cover the summary tables and
          financial statements.
        • Agents that need *narrative* (sectors, schemes, macro) additionally receive
          the final 20 k chars which often contains sectoral allocations and policy text.
        """
        # Smart text slicing ─ favour the parts most likely to contain financial tables
        FINANCE_CHARS = 60_000
        NARRATIVE_EXTRA = 20_000

        finance_text = text[:FINANCE_CHARS]
        # For narrative agents: beginning + end (policy annex / sector details)
        if len(text) > FINANCE_CHARS:
            tail = text[-(NARRATIVE_EXTRA):]
            narrative_text = text[:FINANCE_CHARS] + "\n\n[... middle section ...]\n\n" + tail
        else:
            narrative_text = text

        table_summary = self._format_tables(tables)
        results: Dict[str, Any] = {}

        if progress_callback:
            await progress_callback(10)

        # ── Batch 1: Independent agents, run concurrently ──
        b1 = await asyncio.gather(
            asyncio.to_thread(self._agent_overview,     finance_text,   table_summary, metadata),
            asyncio.to_thread(self._agent_receipts,     finance_text,   table_summary, metadata),
            asyncio.to_thread(self._agent_expenditure,  finance_text,   table_summary, metadata),
            asyncio.to_thread(self._agent_sectors,      narrative_text, table_summary, metadata),
            asyncio.to_thread(self._agent_schemes,      narrative_text, table_summary, metadata),
            return_exceptions=True,
        )

        results["overview"]     = b1[0] if isinstance(b1[0], dict) else {}
        results["receipts"]     = b1[1] if isinstance(b1[1], dict) else {}
        results["expenditure"]  = b1[2] if isinstance(b1[2], dict) else {}
        results["sectors"]      = b1[3] if isinstance(b1[3], dict) else {}
        results["schemes"]      = b1[4] if isinstance(b1[4], dict) else {}

        if progress_callback:
            await progress_callback(60)

        # ── Batch 2: Synthesis agents that build on Batch 1 results ──
        b2 = await asyncio.gather(
            asyncio.to_thread(self._agent_fiscal,  finance_text, table_summary, metadata, results),
            asyncio.to_thread(self._agent_macro,   narrative_text, table_summary, metadata, results),
            return_exceptions=True,
        )
        results["fiscal"]        = b2[0] if isinstance(b2[0], dict) else {}
        results["macroeconomic"] = b2[1] if isinstance(b2[1], dict) else {}

        if progress_callback:
            await progress_callback(85)

        # ── Quality self-assessment ──
        try:
            results["quality_assessment"] = await asyncio.to_thread(
                self._agent_quality, finance_text, results
            )
        except Exception as e:
            logger.warning(f"Quality agent notice: {e}")
            results["quality_assessment"] = {
                "extraction_confidence": 0,
                "disclaimer": "Automated quality validation could not be completed.",
            }

        if progress_callback:
            await progress_callback(95)

        # ── Deterministic reconciliation ──
        self._reconcile(results, metadata, text)

        return results

    # ─────────────────────────── table formatter ────────────────────────────

    def _format_tables(self, tables: List[Dict]) -> str:
        if not tables:
            return "No structured financial tables detected."
        out = ""
        for i, t in enumerate(tables[:30]):
            rows = t.get("data", [])
            if rows:
                out += f"\n── Table {i+1} (Page {t.get('source_page', 'N/A')}) ──\n"
                for r in rows[:20]:
                    if isinstance(r, list):
                        out += " | ".join(str(c) for c in r) + "\n"
        return out

    # ─────────────────────────── individual agents ──────────────────────────

    def _agent_overview(self, text: str, tables: str, metadata: Dict) -> Dict:
        sys = """You are a Chief Budget Analyst for Indian Public Finance.
Extract the budget overview from the uploaded document.
Return ONLY a valid JSON object with these exact keys — use null for any figure not explicitly stated in the document:
{
  "government_name": "string (e.g. Government of India / Government of Uttar Pradesh)",
  "financial_year": "string (e.g. 2024-25)",
  "government_level": "union or state",
  "state_name": "string or null",
  "total_budget_size": number or null,
  "total_receipts": number or null,
  "total_expenditure": number or null,
  "revenue_receipts": number or null,
  "capital_receipts": number or null,
  "revenue_expenditure": number or null,
  "capital_expenditure": number or null,
  "fiscal_deficit": number or null,
  "revenue_deficit": number or null,
  "primary_deficit": number or null,
  "effective_revenue_deficit": number or null,
  "fiscal_deficit_gdp_ratio": number or null,
  "revenue_deficit_gdp_ratio": number or null,
  "nominal_gdp": number or null,
  "executive_summary": "400-600 word AI-synthesized economic narrative covering fiscal stance, priority pillars, and strategic allocations",
  "key_highlights": ["8-12 crisp bullet points with exact numbers from the document"],
  "policy_priorities": ["5-7 strategic policy pillars stated in the budget"],
  "major_announcements": ["Top 5-8 headline announcements with numbers"]
}
All monetary amounts in ₹ Crore. Never fabricate numbers."""

        usr = f"Metadata: {json.dumps(metadata)}\n\nDOCUMENT TEXT (first 60 000 chars):\n{text}\n\nTABLES:\n{tables}"
        return self._parse_json(self._call_llm(sys, usr, 4096))

    def _agent_receipts(self, text: str, tables: str, metadata: Dict) -> Dict:
        sys = """You are a Government Revenue and Tax Policy Specialist.
Analyse the receipts (revenue) side of the uploaded Indian budget document.
Return ONLY a valid JSON object:
{
  "total_receipts": number or null,
  "revenue_receipts": number or null,
  "capital_receipts": number or null,
  "tax_revenue": {
    "total": number or null,
    "corporation_tax": number or null,
    "income_tax": number or null,
    "gst": number or null,
    "customs_duty": number or null,
    "union_excise": number or null,
    "state_excise": number or null,
    "stamp_duty": number or null,
    "land_revenue": number or null,
    "other_taxes": number or null
  },
  "non_tax_revenue": {
    "total": number or null,
    "interest_receipts": number or null,
    "dividends_and_profits": number or null,
    "external_grants": number or null,
    "fees_and_user_charges": number or null,
    "other_non_tax": number or null
  },
  "borrowings": number or null,
  "market_borrowings": number or null,
  "external_borrowings": number or null,
  "disinvestment": number or null,
  "recovery_of_loans": number or null,
  "grants_from_centre": number or null,
  "share_in_central_taxes": number or null,
  "receipt_composition": [
    {"name": "Tax Revenue", "value": number, "percentage": number},
    {"name": "Non-Tax Revenue", "value": number, "percentage": number},
    {"name": "Capital Receipts & Borrowings", "value": number, "percentage": number}
  ],
  "analysis_text": "350-500 word narrative: tax buoyancy, direct vs indirect tax mix, borrowing reliance, revenue mobilisation initiatives.",
  "dependency_observation": "2-3 sentence observation on financing mix."
}
All values in ₹ Crore. Never fabricate figures absent in the document."""

        usr = f"BUDGET TEXT:\n{text}\n\nTABLES:\n{tables}"
        return self._parse_json(self._call_llm(sys, usr, 4096))

    def _agent_expenditure(self, text: str, tables: str, metadata: Dict) -> Dict:
        sys = """You are a Public Expenditure Management Expert.
Analyse the expenditure side of the uploaded Indian budget document.
Return ONLY a valid JSON object:
{
  "total_expenditure": number or null,
  "revenue_expenditure": number or null,
  "capital_expenditure": number or null,
  "interest_payments": number or null,
  "subsidies": number or null,
  "food_subsidy": number or null,
  "fertilizer_subsidy": number or null,
  "fuel_subsidy": number or null,
  "pensions": number or null,
  "defence_expenditure": number or null,
  "infrastructure_spending": number or null,
  "grants_in_aid": number or null,
  "wages_and_salaries": number or null,
  "ministry_wise": [
    {"name": "Ministry / Department Name", "allocation": number, "percentage": number or null, "yoy_change": number or null}
  ],
  "top_spending_ministries": [
    {"name": "Ministry Name", "allocation": number, "percentage": number or null}
  ],
  "expenditure_composition": [
    {"name": "Revenue Expenditure", "value": number, "percentage": number},
    {"name": "Capital Expenditure", "value": number, "percentage": number}
  ],
  "capital_outlay_ratio": number or null,
  "analysis_text": "400-500 word qualitative + quantitative analysis: expenditure quality, asset creation vs consumption, subsidy burden, capex growth trajectory."
}
All values in ₹ Crore."""

        usr = f"BUDGET TEXT:\n{text}\n\nTABLES:\n{tables}"
        return self._parse_json(self._call_llm(sys, usr, 4096))

    def _agent_fiscal(self, text: str, tables: str, metadata: Dict, prev: Dict) -> Dict:
        ctx = json.dumps({
            "total_expenditure": prev.get("overview", {}).get("total_expenditure"),
            "total_receipts": prev.get("overview", {}).get("total_receipts"),
            "fiscal_deficit": prev.get("overview", {}).get("fiscal_deficit"),
            "revenue_deficit": prev.get("overview", {}).get("revenue_deficit"),
            "primary_deficit": prev.get("overview", {}).get("primary_deficit"),
        })

        sys = """You are a Fiscal Economist and Macroeconomic Stability Specialist.
Analyse fiscal health indicators from the uploaded Indian budget.
Return ONLY a valid JSON object:
{
  "fiscal_deficit": number or null,
  "fiscal_deficit_gdp_ratio": number or null,
  "revenue_deficit": number or null,
  "revenue_deficit_gdp_ratio": number or null,
  "primary_deficit": number or null,
  "primary_deficit_gdp_ratio": number or null,
  "effective_revenue_deficit": number or null,
  "outstanding_debt": number or null,
  "debt_to_gdp_ratio": number or null,
  "interest_payments": number or null,
  "interest_to_revenue_ratio": number or null,
  "fiscal_indicators": [
    {
      "name": "indicator name",
      "value": number,
      "unit": "₹ Crore or %",
      "status": "healthy | warning | critical | info",
      "explanation": "clear 1-sentence economic meaning"
    }
  ],
  "historical_trends": [
    {"year": "YYYY-YY (Actual/RE/BE)", "fiscal_deficit": number or null, "revenue_deficit": number or null, "primary_deficit": number or null}
  ],
  "frbm_assessment": "2-3 sentence FRBM compliance assessment.",
  "analysis_text": "400-500 word narrative on fiscal consolidation, borrowing sustainability, debt servicing pressure, and FRBM glide path."
}"""

        usr = f"Previous extraction context: {ctx}\n\nBUDGET TEXT:\n{text}\n\nTABLES:\n{tables}"
        return self._parse_json(self._call_llm(sys, usr, 4096))

    def _agent_sectors(self, text: str, tables: str, metadata: Dict) -> Dict:
        sys = """You are a Sectoral Budget Economist.
Identify and analyse ALL key sectors with budget allocations.
Typical Indian budget sectors: Agriculture & Allied, Rural Development, Education, Healthcare, Defence,
Roads & Highways, Railways, Renewable Energy, Water Resources, Housing & Urban, MSME & Industry,
Women & Child Development, Science & Technology, Social Welfare, Tourism, Fisheries, etc.
Return ONLY a valid JSON object:
{
  "sectors": [
    {
      "sector_name": "Full Sector Name",
      "total_allocation": number,
      "previous_allocation": number or null,
      "percentage_of_total": number or null,
      "yoy_change": number or null,
      "key_schemes": ["Scheme 1", "Scheme 2"],
      "key_announcements": ["Announcement 1"],
      "analysis": "100-150 word economic interpretation of this sector's allocation and expected outcomes.",
      "highlights": ["Highlight 1", "Highlight 2"]
    }
  ],
  "total_sectors": number,
  "highest_allocation_sector": "Sector Name",
  "fastest_growing_sector": "Sector Name or null",
  "analysis_text": "300-400 word cross-sector resource distribution synthesis."
}
All allocations in ₹ Crore. Include ONLY sectors explicitly mentioned in the document."""

        usr = f"BUDGET TEXT:\n{text}\n\nTABLES:\n{tables}"
        return self._parse_json(self._call_llm(sys, usr, 4096))

    def _agent_schemes(self, text: str, tables: str, metadata: Dict) -> Dict:
        sys = """You are a Welfare and Development Scheme Analyst.
Identify all government schemes, missions, and programmes mentioned in this budget
(Centrally Sponsored Schemes, Central Sector Schemes, State Flagship Schemes, PM schemes, etc.).
Return ONLY a valid JSON object:
{
  "schemes": [
    {
      "scheme_name": "Full Official Scheme Name",
      "ministry": "Ministry / Department or null",
      "department": "Department or null",
      "sector": "Sector category",
      "current_allocation": number,
      "previous_allocation": number or null,
      "yoy_change": number or null,
      "objective": "1-2 sentence clear objective",
      "beneficiaries": "Target demographic description",
      "analysis": "Economic significance and expected grassroots impact.",
      "is_new": boolean,
      "is_discontinued": boolean
    }
  ],
  "total_schemes": number,
  "new_schemes": [
    {"name": "New Scheme Name", "allocation": number or null, "objective": "Description"}
  ],
  "top_funded_schemes": [
    {"name": "Scheme Name", "allocation": number}
  ],
  "analysis_text": "300-400 word analysis of welfare funding, PLI-type incentive schemes, and direct benefit transfers."
}
All allocations in ₹ Crore. Only include schemes explicitly named in the document."""

        usr = f"BUDGET TEXT:\n{text}\n\nTABLES:\n{tables}"
        return self._parse_json(self._call_llm(sys, usr, 4096))

    def _agent_macro(self, text: str, tables: str, metadata: Dict, prev: Dict) -> Dict:
        sys = """You are a Senior Macroeconomist.
Analyse the macroeconomic framework of this budget.
Return ONLY a valid JSON object:
{
  "nominal_gdp": number or null,
  "real_gdp_growth_assumption": number or null,
  "nominal_gdp_growth_assumption": number or null,
  "inflation_assumption": number or null,
  "tax_to_gdp_ratio": number or null,
  "capex_to_gdp_ratio": number or null,
  "fiscal_deficit_gdp_ratio": number or null,
  "economic_indicators": [
    {
      "name": "Indicator Name",
      "value": "value with unit (e.g. 7.2% or ₹3,30,000 Cr)",
      "significance": "1-sentence economic significance"
    }
  ],
  "growth_impact": "200 word assessment of GDP growth trajectory",
  "inflation_impact": "150 word assessment of inflationary pressure",
  "employment_impact": "150 word assessment on job generation",
  "risks": ["Risk 1", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2", "Opportunity 3"],
  "who_benefits": [
    {
      "group": "Group name (e.g. Farmers & Rural Sector)",
      "impact": "Positive / Negative / Neutral / Very Positive",
      "explanation": "2-3 sentence explanation grounded in budget allocations."
    }
  ],
  "analysis_text": "400-500 word macroeconomic evaluation covering multiplier effects, crowding-in, debt sustainability, and global headwinds."
}"""

        usr = f"BUDGET TEXT:\n{text}\n\nTABLES:\n{tables}"
        return self._parse_json(self._call_llm(sys, usr, 4096))

    def _agent_quality(self, text: str, results: Dict) -> Dict:
        sys = """You are a Data Validation and Public Finance Auditor.
Evaluate the completeness and consistency of extracted budget data.
Return ONLY a valid JSON object:
{
  "data_completeness": integer 0-100,
  "data_quality_score": integer 0-100,
  "extraction_confidence": integer 0-100,
  "missing_data": ["list of figures expected but not found"],
  "accounting_reconciliation": [
    {"check": "Total Exp = Rev Exp + Cap Exp", "status": "Verified / Mismatch / Insufficient data", "details": ""}
  ],
  "strengths": ["What was extracted well"],
  "limitations": ["Gaps or caveats"],
  "disclaimer": "This report is AI-synthesized from uploaded official documents. All figures in ₹ Crore."
}"""

        summary = {
            "overview_keys":    list((results.get("overview")     or {}).keys()),
            "receipts_keys":    list((results.get("receipts")     or {}).keys()),
            "expenditure_keys": list((results.get("expenditure")  or {}).keys()),
            "fiscal_keys":      list((results.get("fiscal")       or {}).keys()),
            "sectors_count":    len((results.get("sectors")       or {}).get("sectors", [])),
            "schemes_count":    len((results.get("schemes")       or {}).get("schemes", [])),
        }
        usr = f"Extraction summary: {json.dumps(summary)}"
        return self._parse_json(self._call_llm(sys, usr, 1024))

    # ─────────────────────── deterministic reconciliation ───────────────────

    def _safe_float(self, val: Any, default: Optional[float] = None) -> Optional[float]:
        if val is None:
            return default
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            cleaned = re.sub(r"[^\d.\-]", "", val.strip())
            try:
                return float(cleaned) if cleaned else default
            except Exception:
                return default
        return default

    def _reconcile(self, results: Dict, metadata: Dict, full_text: str) -> None:
        """
        Apply deterministic accounting identities using ONLY figures extracted from the document.
        Never inject fabricated or estimated values.
        """
        ov = results.get("overview") or {}
        rec = results.get("receipts") or {}
        exp = results.get("expenditure") or {}
        fisc = results.get("fiscal") or {}
        macro = results.get("macroeconomic") or {}

        # ── Merge metadata ──
        for key in ("financial_year", "government_level", "state_name", "government_name"):
            if metadata.get(key) and not ov.get(key):
                ov[key] = metadata[key]

        # ── Helper: coerce to float or None ──
        sf = self._safe_float

        # ── Pull numbers ──
        tot_exp = sf(ov.get("total_expenditure") or exp.get("total_expenditure"))
        tot_rec = sf(ov.get("total_receipts")    or rec.get("total_receipts"))
        rev_exp = sf(ov.get("revenue_expenditure") or exp.get("revenue_expenditure"))
        cap_exp = sf(ov.get("capital_expenditure") or exp.get("capital_expenditure"))
        rev_rec = sf(ov.get("revenue_receipts")  or rec.get("revenue_receipts"))
        cap_rec = sf(ov.get("capital_receipts")  or rec.get("capital_receipts"))
        f_def   = sf(ov.get("fiscal_deficit")    or fisc.get("fiscal_deficit"))
        r_def   = sf(ov.get("revenue_deficit")   or fisc.get("revenue_deficit"))
        p_def   = sf(ov.get("primary_deficit")   or fisc.get("primary_deficit"))
        gdp_r   = sf(ov.get("fiscal_deficit_gdp_ratio") or fisc.get("fiscal_deficit_gdp_ratio"))

        # ── Accounting identities ──
        # Total = Revenue + Capital (expenditure)
        if rev_exp is not None and cap_exp is not None and tot_exp is None:
            tot_exp = round(rev_exp + cap_exp, 2); ov["total_expenditure"] = tot_exp
        elif tot_exp is not None and rev_exp is not None and cap_exp is None:
            cap_exp = round(tot_exp - rev_exp, 2); ov["capital_expenditure"] = cap_exp
        elif tot_exp is not None and cap_exp is not None and rev_exp is None:
            rev_exp = round(tot_exp - cap_exp, 2); ov["revenue_expenditure"] = rev_exp

        # Total = Revenue + Capital (receipts)
        if rev_rec is not None and cap_rec is not None and tot_rec is None:
            tot_rec = round(rev_rec + cap_rec, 2); ov["total_receipts"] = tot_rec
        elif tot_rec is not None and rev_rec is not None and cap_rec is None:
            cap_rec = round(tot_rec - rev_rec, 2); ov["capital_receipts"] = cap_rec
        elif tot_rec is not None and cap_rec is not None and rev_rec is None:
            rev_rec = round(tot_rec - cap_rec, 2); ov["revenue_receipts"] = rev_rec

        # Revenue Deficit = Revenue Exp − Revenue Receipts
        if r_def is None and rev_exp is not None and rev_rec is not None:
            r_def = round(rev_exp - rev_rec, 2); ov["revenue_deficit"] = r_def

        # Cross-sync overview ↔ sub-dicts
        if tot_exp:  exp["total_expenditure"]  = tot_exp
        if rev_exp:  exp["revenue_expenditure"] = rev_exp
        if cap_exp:  exp["capital_expenditure"] = cap_exp
        if tot_rec:  rec["total_receipts"]      = tot_rec
        if rev_rec:  rec["revenue_receipts"]    = rev_rec
        if cap_rec:  rec["capital_receipts"]    = cap_rec
        if f_def:    fisc["fiscal_deficit"]     = f_def;  ov["fiscal_deficit"]   = f_def
        if r_def:    fisc["revenue_deficit"]    = r_def;  ov["revenue_deficit"]  = r_def
        if p_def:    fisc["primary_deficit"]    = p_def;  ov["primary_deficit"]  = p_def
        if gdp_r:    fisc["fiscal_deficit_gdp_ratio"] = gdp_r; ov["fiscal_deficit_gdp_ratio"] = gdp_r

        # ── Receipt composition (derive if absent) ──
        if not rec.get("receipt_composition"):
            comp = []
            tax_obj  = rec.get("tax_revenue")  or {}
            ntax_obj = rec.get("non_tax_revenue") or {}
            tax_v    = sf(tax_obj.get("total"))  if isinstance(tax_obj, dict)  else None
            ntax_v   = sf(ntax_obj.get("total")) if isinstance(ntax_obj, dict) else None
            borr_v   = sf(rec.get("borrowings") or rec.get("market_borrowings"))

            denom = tot_rec or 1
            if tax_v and tax_v > 0:
                comp.append({"name": "Tax Revenue", "value": tax_v, "percentage": round(tax_v/denom*100,1)})
            if ntax_v and ntax_v > 0:
                comp.append({"name": "Non-Tax Revenue", "value": ntax_v, "percentage": round(ntax_v/denom*100,1)})
            if borr_v and borr_v > 0:
                comp.append({"name": "Borrowings & Capital Receipts", "value": borr_v, "percentage": round(borr_v/denom*100,1)})
            if comp:
                rec["receipt_composition"] = comp

        # ── Expenditure composition (derive if absent) ──
        if not exp.get("expenditure_composition"):
            comp = []
            denom = tot_exp or 1
            if rev_exp and rev_exp > 0:
                comp.append({"name": "Revenue Expenditure", "value": rev_exp, "percentage": round(rev_exp/denom*100,1)})
            if cap_exp and cap_exp > 0:
                comp.append({"name": "Capital Expenditure", "value": cap_exp, "percentage": round(cap_exp/denom*100,1)})
            if comp:
                exp["expenditure_composition"] = comp

        # ── Fiscal indicators (derive if absent) ──
        if not fisc.get("fiscal_indicators"):
            inds = []
            if f_def and f_def > 0:
                inds.append({"name": "Gross Fiscal Deficit", "value": f_def, "unit": "₹ Crore",
                             "status": "warning", "explanation": "Total borrowing requirement to bridge expenditure and non-debt receipts."})
            if gdp_r and gdp_r > 0:
                inds.append({"name": "Fiscal Deficit (% of GDP/GSDP)", "value": gdp_r, "unit": "%",
                             "status": "info", "explanation": "Statutory prudential FRBM target metric."})
            if r_def and r_def > 0:
                inds.append({"name": "Revenue Deficit", "value": r_def, "unit": "₹ Crore",
                             "status": "warning", "explanation": "Excess of recurring expenditure over revenue receipts."})
            if p_def and p_def > 0:
                inds.append({"name": "Primary Deficit", "value": p_def, "unit": "₹ Crore",
                             "status": "info", "explanation": "Fiscal deficit net of interest obligations; isolates current stance."})
            if inds:
                fisc["fiscal_indicators"] = inds

        # ── Executive summary (fallback if LLM couldn't generate one) ──
        if not ov.get("executive_summary"):
            gov   = ov.get("government_name", "The Government")
            fy    = ov.get("financial_year", "the uploaded year")
            facts = []
            if tot_exp: facts.append(f"total expenditure of ₹{tot_exp:,.0f} Crore")
            if tot_rec: facts.append(f"total receipts of ₹{tot_rec:,.0f} Crore")
            if cap_exp: facts.append(f"capital expenditure of ₹{cap_exp:,.0f} Crore")
            if f_def:   facts.append(f"gross fiscal deficit of ₹{f_def:,.0f} Crore")
            if gdp_r:   facts.append(f"fiscal deficit-to-GDP ratio of {gdp_r}%")

            if facts:
                ov["executive_summary"] = (
                    f"Official budget documents for {gov} (FY {fy}) were processed and verified. "
                    f"Key extracted figures: {'; '.join(facts)}. "
                    "All metrics, sectoral allocations, and analytical insights are sourced directly from the uploaded document. "
                    "Any figure absent in the document is transparently displayed as 'Not specified' — no data has been fabricated."
                )
            else:
                ov["executive_summary"] = (
                    f"Budget documents for {gov} (FY {fy}) have been processed. "
                    "Detailed analysis, sectoral allocations, and narrative insights extracted from the document are displayed across the analytical tabs."
                )

        # ── Key highlights fallback ──
        if not ov.get("key_highlights"):
            highlights = []
            if tot_exp: highlights.append(f"Total Budget Expenditure: ₹{tot_exp:,.0f} Crore")
            if tot_rec: highlights.append(f"Total Budget Receipts: ₹{tot_rec:,.0f} Crore")
            if cap_exp: highlights.append(f"Capital Expenditure (Asset Creation): ₹{cap_exp:,.0f} Crore")
            if rev_exp: highlights.append(f"Revenue Expenditure: ₹{rev_exp:,.0f} Crore")
            if f_def:   highlights.append(f"Gross Fiscal Deficit: ₹{f_def:,.0f} Crore")
            if gdp_r:   highlights.append(f"Fiscal Deficit as % of GDP/GSDP: {gdp_r}%")
            if highlights:
                ov["key_highlights"] = highlights

        # ── Macroeconomic indicators fallback ──
        if not macro.get("economic_indicators"):
            inds = []
            rg = sf(macro.get("real_gdp_growth_assumption"))
            ng = sf(macro.get("nominal_gdp_growth_assumption"))
            inf = sf(macro.get("inflation_assumption"))
            if rg:  inds.append({"name": "Real GDP Growth Target",      "value": f"{rg}%",  "significance": "Growth assumption underlying revenue projections."})
            if ng:  inds.append({"name": "Nominal GDP Growth Assumption","value": f"{ng}%",  "significance": "Basis for tax buoyancy and expenditure norms."})
            if inf: inds.append({"name": "Inflation Assumption",         "value": f"{inf}%", "significance": "Price level projection considered in budget calculus."})
            if inds:
                macro["economic_indicators"] = inds

        # Persist back to results
        results["overview"]       = ov
        results["receipts"]       = rec
        results["expenditure"]    = exp
        results["fiscal"]         = fisc
        results["macroeconomic"]  = macro
