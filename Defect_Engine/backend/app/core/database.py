import os
import re
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings


def normalize_database_url(raw_url: str):
    """
    Normalizes database connection URL for PostgreSQL (Supabase) or SQLite.
    Converts standard postgres:// or postgresql:// to postgresql+asyncpg://
    and configures appropriate connect arguments.
    """
    url = raw_url.strip()
    connect_args = {}

    if url.startswith("sqlite+aiosqlite:///./"):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_file_path = os.path.join(base_dir, "defect_engine.db")
        url = f"sqlite+aiosqlite:///{db_file_path}"
        connect_args = {"check_same_thread": False}
    elif "sqlite" in url:
        connect_args = {"check_same_thread": False}
    else:
        # PostgreSQL / Supabase
        if url.startswith("postgres://"):
            url = "postgresql+asyncpg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]

        # Handle sslmode parameter for asyncpg
        # Supabase requires SSL connection and transaction pooler needs statement_cache_size=0
        if "sslmode=require" in url or "supabase" in url or "pooler.supabase.com" in url:
            url = re.sub(r"\?sslmode=[^&]+&?", "?", url)
            url = re.sub(r"&sslmode=[^&]+", "", url)
            url = url.rstrip("?")
            connect_args = {"ssl": True, "statement_cache_size": 0}

    return url, connect_args


db_url, connect_args = normalize_database_url(settings.DATABASE_URL)

engine = create_async_engine(
    db_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    def sync_migrations(connection):
        Base.metadata.create_all(connection)
        
        # Safe column addition for both SQLite and PostgreSQL (Supabase)
        dialect_name = connection.dialect.name
        
        if dialect_name == "sqlite":
            try:
                cursor = connection.connection.cursor()
                cursor.execute("PRAGMA table_info(bug_submissions);")
                columns = [row[1] for row in cursor.fetchall()]
                
                sqlite_columns = [
                    ("root_cause_json", "TEXT"),
                    ("duplicate_json", "TEXT"),
                    ("remediation_json", "TEXT"),
                    ("similar_bugs_json", "TEXT"),
                    ("status", "VARCHAR(50) DEFAULT 'PENDING'"),
                    ("resolved_at", "DATETIME"),
                    ("verified_resolution", "TEXT"),
                    ("is_ingested_to_kb", "BOOLEAN DEFAULT 0"),
                    ("kb_chunk_ids", "TEXT")
                ]
                
                for col_name, col_type in sqlite_columns:
                    if col_name not in columns:
                        cursor.execute(f"ALTER TABLE bug_submissions ADD COLUMN {col_name} {col_type};")
                cursor.close()
            except Exception:
                pass
        elif dialect_name in ["postgresql", "postgres"]:
            pg_columns = [
                ("root_cause_json", "TEXT"),
                ("duplicate_json", "TEXT"),
                ("remediation_json", "TEXT"),
                ("similar_bugs_json", "TEXT"),
                ("status", "VARCHAR(50) DEFAULT 'PENDING'"),
                ("resolved_at", "TIMESTAMP"),
                ("verified_resolution", "TEXT"),
                ("is_ingested_to_kb", "BOOLEAN DEFAULT FALSE"),
                ("kb_chunk_ids", "TEXT")
            ]
            for col_name, col_type in pg_columns:
                try:
                    connection.execute(text(f"ALTER TABLE bug_submissions ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                except Exception:
                    pass

    async with engine.begin() as conn:
        await conn.run_sync(sync_migrations)

