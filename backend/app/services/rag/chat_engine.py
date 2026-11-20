import json
from typing import Dict, Any, List, Optional, AsyncIterator
import structlog
from groq import Groq

from app.core.config import settings
from app.services.rag.vector_store import VectorStoreManager
from app.services.analysis.budget_agents import GROQ_CANDIDATE_MODELS

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are a Senior Government Budget Intelligence Analyst for India.
Your role is to assist policymakers, researchers, economists, journalists, and citizens in deeply understanding Indian Union and State budgets.

RESPONSE FORMAT — always follow this structure:
1. Open with a direct, concise answer (1-3 sentences).
2. Use numbered points or sections for detailed explanation.
3. Quote exact figures from the document in ₹ Crore (e.g. "₹1,61,000 Crore (1.8% of GDP)").
4. If a figure was extracted from a specific page, cite it: "(Source: Page 14, Annual Financial Statement)".
5. Explain financial/economic terminology in plain language when first used.
6. Never hallucinate — if a number is not in the evidence, say so explicitly.
7. Close with 2-3 follow-up questions the user might want to explore.

FORMATTING:
- Use **bold** for key metrics and scheme names.
- Use ### for section headers when the answer has multiple sections.
- Use bullet points (- ) for lists, numbered (1.) for sequential steps.
- Keep monetary values consistently in ₹ Crore with Indian number formatting.
"""

TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "receipts":     ["receipt", "revenue", "tax", "gst", "income", "customs", "excise", "stamp", "non-tax", "disinvestment", "borrowing"],
    "expenditure":  ["expenditure", "spending", "outlay", "ministry", "capex", "capital", "subsidy", "pension", "salary", "grant"],
    "fiscal":       ["deficit", "debt", "borrowing", "frbm", "gdp", "primary deficit", "effective revenue", "fiscal policy"],
    "sectors":      ["sector", "agriculture", "defence", "health", "education", "railway", "road", "energy", "solar", "urban", "rural", "water", "msme", "industry"],
    "schemes":      ["scheme", "yojana", "mgnrega", "pm-kisan", "nrega", "jal", "pmay", "ayushman", "pli", "programme", "mission"],
    "macroeconomic":["gdp", "growth", "inflation", "macro", "employment", "job", "investment", "multiplier", "economy"],
}


class BudgetChatEngine:
    """
    RAG-grounded chat engine for Indian budget Q&A.

    Architecture:
    - Vector store retrieval → top-k document chunks
    - Structured analysis data → relevant section JSON
    - Groq LLM → structured markdown response
    - Rule-based fallback if LLM unavailable
    """

    def __init__(self):
        self.client: Optional[Groq] = None
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                logger.warning(f"Groq client init: {e}")
        self.model = settings.LLM_MODEL
        self.vector_store = VectorStoreManager()

    # ─────────────────────────────── public API ─────────────────────────────

    async def answer_question(
        self,
        workspace_id: str,
        question: str,
        analysis_data: Optional[Dict] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Answer a budget question using RAG + structured analysis data."""

        # 1. Retrieve relevant document chunks from vector store
        chunks = await self.vector_store.search(workspace_id, question, n_results=6)

        # 2. Build rich context combining analysis data + raw document chunks
        rag_context = self._build_context(chunks, analysis_data, question)

        # 3. Call LLM
        if self.client:
            answer = self._call_llm(question, rag_context, context)
            if answer:
                sources = self._format_sources(chunks)
                return {
                    "answer": answer,
                    "sources": sources,
                    "suggested_questions": self._suggest_followups(question, analysis_data),
                }

        # 4. Rule-based fallback
        return self._fallback_answer(question, analysis_data, chunks)

    # ─────────────────────────────── LLM call ───────────────────────────────

    def _call_llm(self, question: str, rag_context: str, view_context: Optional[str]) -> str:
        candidates = []
        for m in [self.model] + GROQ_CANDIDATE_MODELS:
            if m and m not in candidates:
                candidates.append(m)

        user_prompt = f"""USER QUESTION: {question}

VERIFIED BUDGET EVIDENCE (extracted from uploaded official documents):
{rag_context}

{f"CURRENT PAGE CONTEXT: {view_context}" if view_context else ""}

INSTRUCTIONS:
- Answer directly using the evidence above.
- Cite exact ₹ Crore figures. Reference page numbers when available.
- Do NOT invent any figure not in the evidence.
- If a number is missing, state: "This figure was not reported in the uploaded document."
- Use the structured format described in your system prompt."""

        for model_name in candidates:
            try:
                extra_kwargs = {}
                if "qwen3" in model_name.lower():
                    extra_kwargs["extra_body"] = {"thinking": {"type": "disabled"}}

                resp = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": user_prompt},
                    ],
                    temperature=0.15,
                    max_tokens=2000,
                    timeout=20.0,
                    **extra_kwargs,
                )
                content = resp.choices[0].message.content or ""
                if content.strip():
                    logger.info(f"Chat answered by model: {model_name}")
                    return content
            except Exception as e:
                err_str = str(e)
                if "decommissioned" in err_str or "model_not_found" in err_str or "does not exist" in err_str:
                    logger.debug(f"Skipping unavailable model {model_name}")
                else:
                    logger.warning(f"Chat model {model_name} failed: {err_str[:80]}")
                continue

        return ""

    # ─────────────────────────────── context builder ────────────────────────

    def _build_context(
        self,
        chunks: List[Dict],
        analysis_data: Optional[Dict],
        question: str,
    ) -> str:
        parts: List[str] = []
        q = question.lower()

        if analysis_data:
            analysis = analysis_data.get("analysis") or analysis_data  # support both wrapper and raw

            # Always include overview summary (compact)
            overview = analysis.get("overview") or {}
            if overview:
                compact_ov = {
                    k: v for k, v in overview.items()
                    if k not in ("executive_summary",) and v is not None
                }
                parts.append(f"=== Budget Overview ===\n{json.dumps(compact_ov, ensure_ascii=False, default=str)}")

            # Topic-selective deep context
            for topic, kws in TOPIC_KEYWORDS.items():
                if any(kw in q for kw in kws):
                    section = analysis.get(topic) or {}
                    if section:
                        # Truncate large nested lists to avoid token bloat
                        section_compact = self._compact_section(section, topic)
                        parts.append(f"=== {topic.title()} Detail ===\n{json.dumps(section_compact, ensure_ascii=False, default=str)}")

        if chunks:
            parts.append("=== Direct Document Excerpts ===")
            for c in chunks[:5]:
                page = c.get("page", "N/A")
                src  = c.get("source", "Budget Document")
                parts.append(f"[Page {page} | {src}]\n{c.get('text', '')[:600]}")

        return "\n\n".join(parts)

    def _compact_section(self, section: Dict, topic: str) -> Dict:
        """Return a size-limited copy of a section to avoid token overflow."""
        MAX_LIST = 15  # max items for any nested list
        compact = {}
        for k, v in section.items():
            if isinstance(v, list):
                compact[k] = v[:MAX_LIST]
            elif isinstance(v, str) and len(v) > 800:
                compact[k] = v[:800] + "…"
            else:
                compact[k] = v
        return compact

    # ─────────────────────────────── helpers ────────────────────────────────

    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        return [
            {
                "text": c.get("text", "")[:300] + ("…" if len(c.get("text", "")) > 300 else ""),
                "page": c.get("page", "1"),
                "source": c.get("source", "Budget Document"),
                "relevance": round(float(c.get("relevance_score", 0.9)), 2),
            }
            for c in chunks[:4]
        ]

    def _suggest_followups(self, question: str, analysis_data: Optional[Dict]) -> List[str]:
        pool = [
            "What is the total Capital Expenditure vs Revenue Expenditure split?",
            "Which sector received the highest allocation in this budget?",
            "How is the Fiscal Deficit being financed (borrowings vs other sources)?",
            "What are the major direct tax revenue contributors (Income Tax, Corporation Tax)?",
            "Which flagship welfare schemes received significant funding increases?",
            "What is the FRBM compliance status and deficit glide path?",
            "How does capital expenditure compare to previous year?",
            "Which new schemes were announced in this budget?",
            "What is the Revenue Deficit and what does it imply?",
            "What macroeconomic growth assumptions underpin this budget?",
        ]
        q_lower = question.lower()
        # Return questions that don't overlap with the current question
        return [s for s in pool if not any(w in q_lower for w in s.lower().split()[:4])][:3]

    def _fallback_answer(
        self,
        question: str,
        analysis_data: Optional[Dict],
        chunks: List[Dict],
    ) -> Dict[str, Any]:
        """Structured rule-based answer when LLM is unavailable."""
        analysis = (analysis_data or {}).get("analysis") or analysis_data or {}
        overview = analysis.get("overview") or {}

        gov    = overview.get("government_name", "The Government")
        fy     = overview.get("financial_year", "the uploaded financial year")
        tot_exp = overview.get("total_expenditure")
        tot_rec = overview.get("total_receipts")
        f_def   = overview.get("fiscal_deficit")
        gdp_r   = overview.get("fiscal_deficit_gdp_ratio")

        lines = [f"### Budget Summary — {gov} ({fy})\n"]

        def fmt(label, val, unit="Crore"):
            if isinstance(val, (int, float)):
                return f"- **{label}:** ₹{val:,.0f} {unit}"
            return f"- **{label}:** Data not reported in the uploaded document"

        lines += [
            fmt("Total Expenditure", tot_exp),
            fmt("Total Receipts", tot_rec),
            fmt("Gross Fiscal Deficit", f_def),
        ]
        if gdp_r is not None:
            lines.append(f"- **Fiscal Deficit / GDP:** {gdp_r}%")

        exec_sum = overview.get("executive_summary", "")
        if exec_sum:
            lines += ["", "**Key Insight:**", exec_sum[:600]]

        if chunks:
            lines += ["", "**Relevant Document Excerpts:**"]
            for c in chunks[:2]:
                lines.append(f"> _{c.get('text', '')[:350]}…_")

        lines += [
            "",
            "**Suggested follow-up questions:**",
            "1. What are the top 5 spending ministries?",
            "2. How has capital expenditure changed year-on-year?",
            "3. What new schemes were announced in this budget?",
        ]

        return {
            "answer": "\n".join(lines),
            "sources": self._format_sources(chunks),
            "suggested_questions": self._suggest_followups(question, analysis_data),
        }
