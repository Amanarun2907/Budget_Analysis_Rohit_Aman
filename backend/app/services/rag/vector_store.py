import os
import re
import json
import math
from typing import List, Dict, Any, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class VectorStoreManager:
    """
    Document chunking and fast semantic retrieval.

    Storage: JSON files per workspace — zero external dependencies, instant startup,
    no network downloads, works perfectly on Render's ephemeral filesystem.

    Retrieval: TF-IDF keyword scoring — fast, accurate for financial document search
    where queries contain specific numeric/domain terms.

    ChromaDB is intentionally NOT used here because:
    1. It downloads a 79 MB ONNX embedding model on first use — this causes
       17-22 second timeouts on slow cloud networks (Render free tier).
    2. The ONNX model download fails silently and falls back anyway.
    3. For structured financial document search, TF-IDF outperforms
       generic sentence embeddings on domain-specific queries.
    """

    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)

    # ─────────────────────── public interface ───────────────────────────────

    async def index_documents(self, workspace_id: str, text: str, metadata: Dict = None):
        """Chunk text and persist to JSON store."""
        chunks = self._chunk_text(text)
        if not chunks:
            logger.warning(f"No chunks produced for workspace {workspace_id}")
            return

        chunks_path = os.path.join(self.persist_dir, f"{workspace_id}_chunks.json")
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False)

        logger.info(f"Indexed {len(chunks)} chunks for workspace {workspace_id}")

    async def search(self, workspace_id: str, query: str, n_results: int = 6) -> List[Dict]:
        """TF-IDF keyword search over JSON chunk store."""
        return self._tfidf_search(workspace_id, query, n_results)

    # ─────────────────────── TF-IDF search ──────────────────────────────────

    def _tfidf_search(self, workspace_id: str, query: str, n: int = 6) -> List[Dict]:
        """
        TF-IDF ranked search.

        Score(chunk) = Σ_term [ tf(term, chunk) × idf(term, corpus) ]
        where idf = log(N / (df + 1)) + 1

        This reliably ranks chunks containing rare, specific financial terms
        (e.g. "fiscal deficit", "capital outlay", "MGNREGA") higher than
        chunks with only common words.
        """
        path = os.path.join(self.persist_dir, f"{workspace_id}_chunks.json")
        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:
            chunks: List[Dict] = json.load(f)

        if not chunks:
            return []

        # Tokenise — keep 3+ char alphanumeric tokens; lowercase
        query_terms = set(re.findall(r"\b[a-z0-9]{3,}\b", query.lower()))
        if not query_terms:
            return []

        N = len(chunks)

        # Document frequency per term
        df: Dict[str, int] = {}
        for chunk in chunks:
            text_lower = chunk.get("text", "").lower()
            for t in query_terms:
                if t in text_lower:
                    df[t] = df.get(t, 0) + 1

        # Score every chunk
        scored = []
        for chunk in chunks:
            text_lower = chunk.get("text", "").lower()
            score = 0.0
            for t in query_terms:
                tf = text_lower.count(t)
                if tf > 0:
                    idf = math.log(N / (df.get(t, 0) + 1)) + 1
                    score += (1 + math.log(tf)) * idf  # log-normalised TF
            if score > 0:
                scored.append({
                    "text":            chunk.get("text", ""),
                    "page":            chunk.get("page", "1"),
                    "source":          chunk.get("source", ""),
                    "section":         chunk.get("section", ""),
                    "relevance_score": round(score, 3),
                })

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:n]

    # ─────────────────────── text chunking ──────────────────────────────────

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 1200,
        overlap: int = 250,
    ) -> List[Dict]:
        """
        Split document text into overlapping chunks, tracking page numbers,
        source file name, and section headings for citation-quality retrieval.

        Markers injected by DocumentProcessor:
        - '--- Page N ---'       → updates current page
        - '=== Document: X ==='  → updates current source file
        """
        if not text:
            return []

        PAGE_PATTERN    = re.compile(r"---\s*Page\s+(\d+)\s*---")
        SOURCE_PATTERN  = re.compile(r"===\s*Document:\s*(.+?)\s*===")
        SECTION_PATTERN = re.compile(
            r"\b(Part\s+[IVX]+|Section\s+\d+|Chapter\s+\d+|"
            r"STATEMENT\s+[IVX]+|ANNEX[UE]RE?\s*[A-Z\d]+|APPENDIX\s+[A-Z\d]+)\b",
            re.IGNORECASE,
        )

        current_page    = 1
        current_source  = ""
        current_section = ""
        current_chunk   = ""
        chunk_index     = 0
        chunks: List[Dict] = []

        for line in text.split("\n"):
            pm = PAGE_PATTERN.search(line)
            if pm:
                current_page = int(pm.group(1))
                continue

            sm = SOURCE_PATTERN.search(line)
            if sm:
                current_source = sm.group(1).strip()
                continue

            sec_m = SECTION_PATTERN.search(line)
            if sec_m:
                current_section = sec_m.group(0).strip()

            current_chunk += line + "\n"

            if len(current_chunk) >= chunk_size:
                stripped = current_chunk.strip()
                if stripped:
                    chunks.append({
                        "index":   chunk_index,
                        "text":    stripped,
                        "page":    current_page,
                        "source":  current_source,
                        "section": current_section,
                    })
                    chunk_index += 1
                current_chunk = current_chunk[-overlap:]

        stripped = current_chunk.strip()
        if stripped:
            chunks.append({
                "index":   chunk_index,
                "text":    stripped,
                "page":    current_page,
                "source":  current_source,
                "section": current_section,
            })

        return chunks
