import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Software Defect Analysis & Multi-Agent Triage Engine"
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # CORS: Allows local Next.js dev server, Vercel deployments, and custom domains
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    # Database Settings: Defaults to local SQLite, easily overridden with Supabase PostgreSQL URL
    DATABASE_URL: str = "sqlite+aiosqlite:///./defect_engine.db"

    # Vector DB Settings
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # LLM Settings (Optional)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: str = "60/minute"
    SUBMISSION_RATE_LIMIT: str = "15/minute"
    SEARCH_RATE_LIMIT: str = "30/minute"
    ANALYTICS_RATE_LIMIT: str = "30/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
