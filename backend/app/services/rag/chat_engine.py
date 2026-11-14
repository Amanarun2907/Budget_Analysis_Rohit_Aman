import json
from typing import Dict, Any, List, Optional
import structlog
from groq import Groq

from app.core.config import settings
from app.services.rag.vector_store import VectorStoreManager

logger = structlog.get_logger()

class BudgetChatEngine:
    """AI-powered chat engine for budget Q&A grounded in document evidence and structured financial figures."""
    
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                logger.warning(f"Groq client init error: {e}")
        self.model = settings.LLM_MODEL
        self.vector_store = VectorStoreManager()
    
    async def answer_question(
        self,
        workspace_id: str,
        question: str,
        analysis_data: Optional[Dict] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Answer a budget question using RAG + analysis data."""
        
        # 1. Retrieve relevant document chunks
        relevant_chunks = await self.vector_store.search(workspace_id, question, n_results=5)
        
        # 2. Build context from analysis data and retrieved chunks
        rag_context = self._build_context(relevant_chunks, analysis_data, question)
        
        # 3. If Groq client is configured, call LLM with candidate models
        if self.client:
            candidate_models = []
            for m in [self.model, "qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
                if m and m not in candidate_models:
                    candidate_models.append(m)
            
            system_prompt = self._get_system_prompt()
            user_prompt = f"""USER QUESTION: {question}

VERIFIED BUDGET EVIDENCE & EXTRACTED DATA:
{rag_context}

{f'USER SELECTION / VIEW CONTEXT: {context}' if context else ''}

Instructions:
1. Answer the question directly and comprehensively using the provided budget data.
2. Cite exact numerical figures (in ₹ Crore or relevant percentages).
3. If page numbers or tables exist in the evidence, reference them (e.g. "as reported on Page 14").
4. Explain financial terminology simply (e.g., Fiscal Deficit, Capital Outlay, Devolution).
5. Never invent figures that do not exist in the evidence. If a number is absent, explicitly state that it was not reported in the document.
6. Provide structured bullet points where helpful.
7. End with 2-3 logical follow-up questions."""

            for model_name in candidate_models:
                try:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.2,
                        max_tokens=4000,
                    )
                    
                    answer = response.choices[0].message.content or ""
                    if answer.strip():
                        sources = [
                            {
                                "text": chunk["text"][:250] + ("..." if len(chunk["text"]) > 250 else ""),
                                "page": chunk.get("page", "1"),
                                "source": chunk.get("source", "Budget Document"),
                                "relevance": round(float(chunk.get("relevance_score", 0.9)), 2),
                            }
                            for chunk in relevant_chunks[:3]
                        ]
                        
                        suggested = self._generate_suggestions(question, analysis_data)
                        
                        return {
                            "answer": answer,
                            "sources": sources,
                            "suggested_questions": suggested,
                        }
                except Exception as e:
                    logger.warning(f"Chat model {model_name} failed: {e}. Trying next...")
                    continue
        
        # Fallback intelligent answer if LLM call fails or key is missing
        return self._generate_rule_based_answer(question, analysis_data, relevant_chunks)
    
    def _get_system_prompt(self) -> str:
        return """You are the Senior Chief Economist and Government Budget Intelligence Analyst.
You assist policymakers, researchers, financial analysts, journalists, and citizens in understanding Indian Union and State budgets.
Your communication style is clear, authoritative, highly structured, and economically sound.
Always preserve monetary units (e.g. ₹ Crore) and distinct accounting classifications (Budget Estimate BE, Revised Estimate RE, Actuals).
Never hallucinate numbers. Point out economic trade-offs, fiscal implications, and sectoral priorities."""

    def _build_context(self, chunks: List[Dict], analysis_data: Optional[Dict], question: str) -> str:
        context_parts = []
        
        if analysis_data:
            overview = analysis_data.get("overview", {})
            if overview:
                context_parts.append(f"Budget Overview Summary: {json.dumps(overview, default=str)}")
            
            q_lower = question.lower()
            if any(k in q_lower for k in ["receipt", "revenue", "tax", "gst", "income"]):
                receipts = analysis_data.get("receipts", {})
                if receipts:
                    context_parts.append(f"Receipts Detail: {json.dumps(receipts, default=str)}")
            
            if any(k in q_lower for k in ["expenditure", "spending", "ministry", "capex", "capital"]):
                exp = analysis_data.get("expenditure", {})
                if exp:
                    context_parts.append(f"Expenditure Detail: {json.dumps(exp, default=str)}")
            
            if any(k in q_lower for k in ["deficit", "debt", "borrowing", "fiscal", "gdp"]):
                fiscal = analysis_data.get("fiscal", {})
                if fiscal:
                    context_parts.append(f"Fiscal Health & Deficit: {json.dumps(fiscal, default=str)}")
            
            if any(k in q_lower for k in ["sector", "agriculture", "defence", "health", "education", "rail"]):
                sectors = analysis_data.get("sectors", {})
                if sectors:
                    context_parts.append(f"Sector Allocations: {json.dumps(sectors, default=str)}")
            
            if any(k in q_lower for k in ["scheme", "yojana", "mgnrega", "pm-kisan", "program"]):
                schemes = analysis_data.get("schemes", {})
                if schemes:
                    context_parts.append(f"Schemes & Initiatives: {json.dumps(schemes, default=str)}")
        
        if chunks:
            context_parts.append("Direct Text Excerpts from Uploaded Documents:")
            for c in chunks:
                context_parts.append(f"[Page {c.get('page', 'N/A')}] {c.get('text', '')}")
        
        return "\n\n".join(context_parts)
    
    def _generate_rule_based_answer(self, question: str, analysis_data: Optional[Dict], chunks: List[Dict]) -> Dict:
        """Deterministic answer generator when external LLM is offline."""
        overview = (analysis_data or {}).get("overview", {})
        total_exp = overview.get("total_expenditure", "N/A")
        total_rec = overview.get("total_receipts", "N/A")
        fiscal_def = overview.get("fiscal_deficit", "N/A")
        fy = overview.get("financial_year", "the budget")
        gov = overview.get("government_name", "the government")
        
        ans = f"### Budget Analysis for {gov} ({fy})\n\n"
        ans += f"- **Total Expenditure:** ₹{total_exp:,} Crore\n" if isinstance(total_exp, (int, float)) else f"- **Total Expenditure:** {total_exp}\n"
        ans += f"- **Total Receipts:** ₹{total_rec:,} Crore\n" if isinstance(total_rec, (int, float)) else f"- **Total Receipts:** {total_rec}\n"
        ans += f"- **Fiscal Deficit:** ₹{fiscal_def:,} Crore\n" if isinstance(fiscal_def, (int, float)) else f"- **Fiscal Deficit:** {fiscal_def}\n\n"
        
        if overview.get("executive_summary"):
            ans += f"**Key Executive Summary:**\n{overview.get('executive_summary')}\n\n"
        
        if chunks:
            ans += "**Relevant Document Evidence:**\n"
            for c in chunks[:2]:
                ans += f"> {c.get('text', '')[:300]}...\n\n"
        
        return {
            "answer": ans,
            "sources": [{"text": c.get("text", "")[:200], "page": c.get("page", "1"), "source": c.get("source", "Document")} for c in chunks[:3]],
            "suggested_questions": self._generate_suggestions(question, analysis_data),
        }
    
    def _generate_suggestions(self, question: str, analysis_data: Optional[Dict]) -> List[str]:
        suggestions = [
            "What is the total Capital Expenditure versus Revenue Expenditure?",
            "What are the top 5 sectors with highest allocations?",
            "How is the Fiscal Deficit financed (market borrowings vs other sources)?",
            "What are the major tax revenue contributors (GST, Income Tax, Corp Tax)?",
            "Which welfare schemes received increased funding this financial year?",
        ]
        q_lower = question.lower()
        return [s for s in suggestions if not any(w in q_lower for w in s.lower().split()[:3])][:3]

