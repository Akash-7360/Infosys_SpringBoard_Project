import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "historical_defects"


class VectorStoreService:
    def __init__(self, persist_dir: str = settings.CHROMA_PERSIST_DIR):
        abs_persist_dir = os.path.abspath(persist_dir)
        os.makedirs(abs_persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=abs_persist_dir)
        
        try:
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL_NAME
            )
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to DefaultEmbeddingFunction.")
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def chunk_defect_record(self, bug_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Implements 3-Chunk Ingestion Strategy:
        Chunk 1: Bug Title + Functional Description
        Chunk 2: Error Trace + Offending Function Call
        Chunk 3: Verified Root Cause + Resolution Patch
        """
        bug_id = bug_record.get("bug_id", "UNKNOWN")
        repo = bug_record.get("repository", "General")
        component = bug_record.get("component", "General")
        title = bug_record.get("title", "")
        desc = bug_record.get("description", "")
        trace = bug_record.get("stack_trace", "")
        offending_func = bug_record.get("offending_function", "N/A")
        root_cause = bug_record.get("root_cause", "")
        resolution = bug_record.get("resolution", "")

        chunks = []

        # Chunk 1: Bug Title + Functional Description
        chunk1_text = f"Bug ID: {bug_id}\nRepository: {repo}\nComponent: {component}\nTitle: {title}\nDescription: {desc}".strip()
        chunks.append({
            "chunk_id": f"{bug_id}_chunk1_overview",
            "text": chunk1_text,
            "metadata": {
                "bug_id": bug_id,
                "chunk_type": "overview",
                "repository": repo,
                "component": component,
                "title": title,
                "resolution": resolution,
                "root_cause": root_cause,
                "offending_function": offending_func
            }
        })

        # Chunk 2: Error Trace + Offending Function Call
        chunk2_text = f"Bug ID: {bug_id}\nOffending Function: {offending_func}\nStack Trace:\n{trace}".strip()
        chunks.append({
            "chunk_id": f"{bug_id}_chunk2_trace",
            "text": chunk2_text,
            "metadata": {
                "bug_id": bug_id,
                "chunk_type": "stack_trace",
                "repository": repo,
                "component": component,
                "title": title,
                "resolution": resolution,
                "root_cause": root_cause,
                "offending_function": offending_func
            }
        })

        # Chunk 3: Verified Root Cause + Resolution Patch
        chunk3_text = f"Bug ID: {bug_id}\nVerified Root Cause: {root_cause}\nResolution & Patch:\n{resolution}".strip()
        chunks.append({
            "chunk_id": f"{bug_id}_chunk3_resolution",
            "text": chunk3_text,
            "metadata": {
                "bug_id": bug_id,
                "chunk_type": "resolution",
                "repository": repo,
                "component": component,
                "title": title,
                "resolution": resolution,
                "root_cause": root_cause,
                "offending_function": offending_func
            }
        })

        return chunks

    def add_defects(self, defects_list: List[Dict[str, Any]]) -> int:
        """
        Indexes defect records into ChromaDB using the 3-Chunking strategy.
        """
        ids = []
        documents = []
        metadatas = []

        for bug in defects_list:
            chunks = self.chunk_defect_record(bug)
            for chunk in chunks:
                ids.append(chunk["chunk_id"])
                documents.append(chunk["text"])
                metadatas.append(chunk["metadata"])

        if ids:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        return len(ids)

    def search_similar(
        self,
        query_text: str,
        top_k: int = 5,
        repository: Optional[str] = None,
        component: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid cosine semantic search over historical defect dataset with optional repo/component filters.
        """
        if not query_text or self.collection.count() == 0:
            return []

        filters = []
        if repository and repository.strip() and repository not in ["All", "General", "Mozilla/Apache/Eclipse"]:
            filters.append({"repository": repository.strip()})

        where_filter = filters[0] if filters else None

        # Execute query
        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(top_k * 3, self.collection.count()), # Retrieve enough chunks to deduplicate by bug_id
            where=where_filter if where_filter else None
        )

        seen_bugs = set()
        deduped_results = []

        if results and results.get("ids") and len(results["ids"]) > 0:
            doc_ids = results["ids"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else []
            distances = results["distances"][0] if results.get("distances") else []
            documents = results["documents"][0] if results.get("documents") else []

            for i in range(len(doc_ids)):
                meta = metadatas[i] if i < len(metadatas) else {}
                bug_id = meta.get("bug_id", "UNKNOWN")
                
                # Cosine distance conversion to similarity percentage [0..1]
                dist = distances[i] if i < len(distances) else 0.5
                similarity_score = max(0.0, min(1.0, 1.0 - (dist / 2.0)))

                if bug_id not in seen_bugs:
                    seen_bugs.add(bug_id)
                    deduped_results.append({
                        "bug_id": bug_id,
                        "repository": meta.get("repository", "General"),
                        "component": meta.get("component", "General"),
                        "title": meta.get("title", ""),
                        "description": documents[i] if i < len(documents) else "",
                        "stack_trace": documents[i] if meta.get("chunk_type") == "stack_trace" else "",
                        "resolution": meta.get("resolution", ""),
                        "root_cause": meta.get("root_cause", ""),
                        "offending_function": meta.get("offending_function", ""),
                        "similarity_score": round(similarity_score, 4)
                    })

                if len(deduped_results) >= top_k:
                    break

        return deduped_results


# Global singleton instance
vector_store_service = VectorStoreService()
