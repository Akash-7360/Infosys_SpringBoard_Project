from typing import List, Dict, Any, Optional
from app.services.vector_store import vector_store_service


class RAGPipelineService:
    def __init__(self):
        self.vector_store = vector_store_service

    def retrieve_similar_defects(
        self,
        title: str,
        description: str,
        stack_trace: str,
        repository: Optional[str] = None,
        component: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes defect query string from title, description, and stack trace,
        then retrieves top-k historical defects with verified resolutions from ChromaDB.
        """
        combined_query = f"{title}\n{description}\n{stack_trace[:300] if stack_trace else ''}".strip()
        
        similar_defects = self.vector_store.search_similar(
            query_text=combined_query,
            top_k=top_k,
            repository=repository,
            component=component
        )
        
        return similar_defects

    def format_rag_context_for_agent(self, similar_defects: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved historical defects into clean context string for Root Cause synthesis.
        """
        if not similar_defects:
            return "No historical defect matches found in vector knowledge base."

        context_lines = []
        for idx, bug in enumerate(similar_defects, 1):
            context_lines.append(
                f"--- Historical Match #{idx} [{bug.get('repository')}/{bug.get('component')}] ---\n"
                f"Bug ID: {bug.get('bug_id')}\n"
                f"Title: {bug.get('title')}\n"
                f"Similarity Score: {int(bug.get('similarity_score', 0) * 100)}%\n"
                f"Verified Root Cause: {bug.get('root_cause') or 'N/A'}\n"
                f"Verified Resolution / Fix:\n{bug.get('resolution')}\n"
            )
        return "\n".join(context_lines)


rag_pipeline_service = RAGPipelineService()
