import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.models.bug_submission import SystemicPatternAnalytics
from app.services.pattern_analytics import generate_defect_pattern_analytics

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/patterns", response_model=SystemicPatternAnalytics)
@limiter.limit(settings.ANALYTICS_RATE_LIMIT)
async def get_defect_pattern_analytics(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Milestone 4: Defect Pattern Analytics Module.
    Identifies recurring bug themes, high-frequency affected components,
    systemic issue patterns, hotspots, defect health score, and architectural recommendations
    across all submitted bugs.
    """
    analytics = await generate_defect_pattern_analytics(db)
    return analytics
