from fastapi import APIRouter
from app.api.v1.submissions import router as submissions_router
from app.api.v1.search import router as search_router
from app.api.v1.analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(submissions_router, prefix="/bugs", tags=["Defect Submissions & Analysis"])
api_router.include_router(search_router, prefix="/bugs", tags=["Vector Semantic Search"])
api_router.include_router(analytics_router, prefix="/bugs/analytics", tags=["Defect Pattern Analytics"])
