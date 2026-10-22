import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.limiter import limiter
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("defect_engine")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables (Supabase PostgreSQL / SQLite)...")
    await init_db()
    logger.info("Database initialized successfully.")

    # Auto-seed ChromaDB knowledge base if empty (critical for Render cloud deployment)
    try:
        from app.services.vector_store import vector_store_service
        from scripts.seed_historical_data import seed_vector_db
        if vector_store_service.collection.count() == 0:
            logger.info("ChromaDB is empty. Auto-seeding baseline historical defects for RAG...")
            seed_vector_db()
            logger.info("ChromaDB baseline defect seeding complete.")
    except Exception as e:
        logger.warning(f"Could not verify/seed ChromaDB on startup: {e}")

    yield
    logger.info("Shutting down Defect Engine application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Rate Limiter State & Middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)
    limit = getattr(request.state, "view_rate_limit", None)
    if limit:
        try:
            stats = limiter.limiter.get_window_stats(limit[0], *limit[1])
            response.headers["X-RateLimit-Limit"] = str(limit[0])
            response.headers["X-RateLimit-Remaining"] = str(stats.remaining)
            response.headers["X-RateLimit-Reset"] = str(int(stats.reset_time))
        except Exception:
            response.headers["X-RateLimit-Limit"] = str(limit[0])
    return response


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Standardized HTTP 429 Too Many Requests response with Retry-After header.
    """
    retry_after = getattr(exc, "retry_after", 60)
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Allowed rate limit: {exc.detail}",
            "retry_after_seconds": retry_after,
            "path": request.url.path
        },
        headers={
            "Retry-After": str(retry_after)
        }
    )


# CORS Setup: Supports localhost, Render, and Vercel cloud frontend deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
@limiter.limit("120/minute")
def root(request: Request):
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health")
@limiter.limit("120/minute")
def health_check(request: Request):
    return {"status": "healthy"}
