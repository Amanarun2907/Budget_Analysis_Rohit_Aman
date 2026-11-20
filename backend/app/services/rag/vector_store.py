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
    Document chunking and semantic retrieval.

    Storage strategy (two layers):
    1. ChromaDB (persistent) — used when chromadb package is available; provides
       cosine-similarity search over dense embeddings.
    2. JSON fallback — always written; used if ChromaDB is unavailable.  Retrieval
       uses a lightweight TF-IDF-inspired keyword scorer (fast, zero-dependency).
    """

    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)

    # ─────────────────────── ChromaDB helpers ───────────────────────────────

    def _get_collection(self, workspace_id: str):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.persist_dir)
            # Collection names: alphanumeric + underscore/hyphen, max 63 chars
            name = re.sub(r"[^a-zA-Z0-9_-]", "_", f"budget_{workspace_id}")[:63]
            return client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            logger.debug(f"ChromaDB unavailable ({e}); will use JSON fallback")
            return None

    # ─────────────────────── public interface ───────────────────────────────

    async def index_documents(self, workspace_id: str, text: str, metadata: Dict = None):
        """Chunk text, store in ChromaDB (if available), always write JSON fallback."""
        chunks = self._chunk_text(text)
        if not chunks:
            return

        # Always persist JSON (guarantees fallback works on cold start)
        chunks_path = os.path.join(self.persist_dir, f"{workspace_id}_chunks.json")
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False)

        collection = self._get_collection(workspace_id)
        if collection:
            try:
                ids       = [f"{workspace_id}_{i}" for i in range(len(chunks))]
                documents = [c["text"] for c in chunks]
                metas     = [
                    {
                        "chunk_index": c["index"],
                        "page":        str(c.get("page", "1")),
                        "source":      str(c.get("source", "budget")),
                        "workspace_id": workspace_id,
                        "section":     str(c.get("section", "")),
                    }
                    for c in chunks
                ]

                BATCH = 80
                for i in range(0, len(documents), BATCH):
                    collection.upsert(
                        ids=ids[i:i+BATCH],
                        documents=documents[i:i+BATCH],
                        metadatas=metas[i:i+BATCH],
                    )
                logger.info(f"Indexed {len(chunks)} chunks in ChromaDB for workspace {workspace_id}")
            except Exception as e:
                logger.warning(f"ChromaDB indexing error (JSON fallback active): {e}")

    async def search(self, workspace_id: str, query: str, n_results: int = 6) -> List[Dict]:
        """Search for relevant chunks; prefers ChromaDB, falls back to keyword scoring."""
        collection = self._get_collection(workspace_id)
        if collection:
            try:
                res = collection.query(query_texts=[query], n_results=min(n_results, 15))
                if res and res.get("documents") and res["documents"][0]:
                    return [
                        {
                            "text":            doc,
                            "page":            (res.get("metadatas") or [[]])[0][i].get("page", "1"),
                            "source":          (res.get("metadatas") or [[]])[0][i].get("source", ""),
                            "section":         (res.get("metadatas") or [[]])[0][i].get("section", ""),
                            "relevance_score": max(0.0, 1.0 - (res.get("distances") or [[0.5]])[0][i]),
                        }
                        for i, doc in enumerate(res["documents"][0])
                    ]
            except Exception as e:
                logger.warning(f"ChromaDB search failed ({e}); using keyword fallback")

        return self._keyword_search(workspace_id, query, n_results)

    # ─────────────────────── keyword fallback ───────────────────────────────

    def _keyword_search(self, workspace_id: str, query: str, n: int = 6) -> List[Dict]:
        """
        TF-IDF-inspired keyword search over the JSON chunk store.

        Score = sum of (term_freq_in_chunk × log(total_chunks / doc_freq + 1))
        This rewards chunks containing rare query terms more than common ones.
        """
        path = os.path.join(self.persist_dir, f"{workspace_id}_chunks.json")
        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:
            chunks: List[Dict] = json.load(f)

        if not chunks:
            return []

        # Tokenise query
        query_terms = set(re.findall(r"\b\w{3,}\b", query.lower()))
        if not query_terms:
            return []

        N = len(chunks)

        # Document-frequency per term
        df: Dict[str, int] = {}
        for chunk in chunks:
            text_lower = chunk.get("text", "").lower()
            for t in query_terms:
                if t in text_lower:
                    df[t] = df.get(t, 0) + 1

        # Score chunks
        scored = []
        for chunk in chunks:
            text_lower = chunk.get("text", "").lower()
            score = 0.0
            for t in query_terms:
                tf = text_lower.count(t)
                if tf > 0:
                    idf = math.log((N / (df.get(t, 1) + 1)) + 1)
                    score += tf * idf
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
        Split document text into overlapping chunks, tracking page numbers and source file.

        Markers injected by DocumentProcessor:
        - '--- Page N ---'       → updates current page
        - '=== Document: X ==='  → updates current source file
        """
        if not text:
            return []

        PAGE_PATTERN   = re.compile(r"---\s*Page\s+(\d+)\s*---")
        SOURCE_PATTERN = re.compile(r"===\s*Document:\s*(.+?)\s*===")
        SECTION_PATTERN = re.compile(
            r"(Part\s+[IVX]+|Section\s+\d+|Chapter\s+\d+|STATEMENT\s+[IVX]+|"
            r"ANNEX[UE]RE?\s*[A-Z\d]+|APPENDIX\s+[A-Z\d]+)",
            re.IGNORECASE,
        )

        current_page   = 1
        current_source = ""
        current_section = ""
        current_chunk  = ""
        chunk_index    = 0
        chunks: List[Dict] = []

        lines = text.split("\n")
        for line in lines:
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
                # Overlap: keep last `overlap` chars
                current_chunk = current_chunk[-overlap:]

        # Final chunk
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
