import os
import re
from typing import List, Dict, Any, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()

class VectorStoreManager:
    """Manages document chunking and vector storage with ChromaDB and semantic retrieval."""
    
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
    
    def _get_collection(self, workspace_id: str):
        """Get or create a ChromaDB collection for a workspace."""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.persist_dir)
            collection_name = f"budget_{workspace_id[:40]}"
            # ChromaDB requires alphanumeric, underscore or hyphen
            collection_name = re.sub(r'[^a-zA-Z0-9_-]', '_', collection_name)
            return client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            # Clean fallback to fast indexed JSON store
            return None
    
    async def index_documents(self, workspace_id: str, text: str, metadata: Dict = None):
        """Index document text into vector store with chunking."""
        collection = self._get_collection(workspace_id)
        chunks = self._chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        
        if not chunks:
            return
        
        if collection:
            try:
                ids = [f"{workspace_id}_{i}" for i in range(len(chunks))]
                documents = [chunk["text"] for chunk in chunks]
                metadatas = [
                    {
                        "chunk_index": chunk["index"],
                        "page": str(chunk.get("page", "1")),
                        "source": str(chunk.get("source", "budget")),
                        "workspace_id": workspace_id,
                    }
                    for chunk in chunks
                ]
                
                # Batch add to avoid payload limits
                batch_size = 80
                for i in range(0, len(documents), batch_size):
                    batch_end = min(i + batch_size, len(documents))
                    collection.upsert(
                        ids=ids[i:batch_end],
                        documents=documents[i:batch_end],
                        metadatas=metadatas[i:batch_end],
                    )
                logger.info(f"Indexed {len(chunks)} chunks in ChromaDB for workspace {workspace_id}")
            except Exception as e:
                logger.warning(f"Error indexing in ChromaDB: {e}")
        
        # Also persist chunks to simple JSON file for ultra-fast local keyword & semantic retrieval fallback
        try:
            chunks_file = os.path.join(self.persist_dir, f"{workspace_id}_chunks.json")
            import json
            with open(chunks_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save local chunks json: {e}")
    
    async def search(self, workspace_id: str, query: str, n_results: int = 5) -> List[Dict]:
        """Search for relevant document chunks using ChromaDB with keyword-scoring fallback."""
        collection = self._get_collection(workspace_id)
        if collection:
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=min(n_results, 10),
                )
                if results and results.get("documents") and len(results["documents"][0]) > 0:
                    chunks = []
                    for i, doc in enumerate(results["documents"][0]):
                        meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                        distance = results["distances"][0][i] if results.get("distances") else 0.5
                        chunks.append({
                            "text": doc,
                            "metadata": meta,
                            "relevance_score": max(0.0, 1.0 - distance),
                            "page": meta.get("page", "1"),
                            "source": meta.get("source", ""),
                        })
                    return chunks
            except Exception as e:
                logger.warning(f"ChromaDB search failed, using text search fallback: {e}")
        
        # Local fallback text search
        return self._keyword_search_fallback(workspace_id, query, n_results)
    
    def _keyword_search_fallback(self, workspace_id: str, query: str, n_results: int = 5) -> List[Dict]:
        chunks_file = os.path.join(self.persist_dir, f"{workspace_id}_chunks.json")
        if not os.path.exists(chunks_file):
            return []
        
        import json
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        keywords = set(re.findall(r'\w+', query.lower()))
        scored_chunks = []
        for chunk in chunks:
            text_lower = chunk["text"].lower()
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scored_chunks.append({
                    "text": chunk["text"],
                    "page": chunk.get("page", "1"),
                    "source": chunk.get("source", ""),
                    "relevance_score": float(score),
                })
        
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_chunks[:n_results]
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split text into overlapping chunks with page tracking."""
        if not text:
            return []
        
        chunks = []
        current_page = 1
        current_source = ""
        
        page_pattern = r'--- Page (\d+) ---'
        source_pattern = r'=== Document: (.+?) ==='
        
        lines = text.split('\n')
        current_chunk = ""
        chunk_index = 0
        
        for line in lines:
            p_match = re.search(page_pattern, line)
            if p_match:
                current_page = int(p_match.group(1))
                continue
            
            s_match = re.search(source_pattern, line)
            if s_match:
                current_source = s_match.group(1)
                continue
            
            current_chunk += line + "\n"
            
            if len(current_chunk) >= chunk_size:
                chunks.append({
                    "index": chunk_index,
                    "text": current_chunk.strip(),
                    "page": current_page,
                    "source": current_source,
                })
                chunk_index += 1
                current_chunk = current_chunk[-overlap:]
        
        if current_chunk.strip():
            chunks.append({
                "index": chunk_index,
                "text": current_chunk.strip(),
                "page": current_page,
                "source": current_source,
            })
        
        return chunks

