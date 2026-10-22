from fastapi import APIRouter, Request
from app.core.config import settings
from app.core.limiter import limiter
from app.models.bug_submission import (
    SimilarBugSearchRequest,
    SimilarBugResponse,
    HistoricalBugItem
)
from app.services.vector_store import vector_store_service

router = APIRouter()


@router.post("/search-similar", response_model=SimilarBugResponse)
@limiter.limit(settings.SEARCH_RATE_LIMIT)
async def search_similar_defects(request: Request, req: SimilarBugSearchRequest):
    """
    Performs hybrid cosine semantic search over historical bug database
    with repository and component metadata filtering.
    """
    raw_results = vector_store_service.search_similar(
        query_text=req.query_text,
        top_k=req.top_k,
        repository=req.repository,
        component=req.component
    )

    items = [
        HistoricalBugItem(
            bug_id=res.get("bug_id", ""),
            repository=res.get("repository", "General"),
            component=res.get("component", "General"),
            title=res.get("title", ""),
            description=res.get("description", ""),
            stack_trace=res.get("stack_trace", ""),
            resolution=res.get("resolution", ""),
            similarity_score=res.get("similarity_score", 0.0)
        )
        for res in raw_results
    ]

    return SimilarBugResponse(
        query=req.query_text,
        total_found=len(items),
        results=items
    )
