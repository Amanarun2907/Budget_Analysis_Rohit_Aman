from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base

# Async engine for FastAPI endpoints
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
else:
    engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=20, max_overflow=10)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _run_migrations(sync_engine):
    """
    Safe additive migrations — adds new columns to existing tables without destroying data.
    Uses IF NOT EXISTS / try-except so it's idempotent across all deployments.
    """
    migrations = [
        # BudgetDocument: add alias columns added in v1.1
        "ALTER TABLE budget_documents ADD COLUMN stored_filename TEXT",
        "ALTER TABLE budget_documents ADD COLUMN file_size_bytes INTEGER",
        # BudgetDocument: add updated_at if missing
        "ALTER TABLE budget_documents ADD COLUMN updated_at DATETIME",
    ]

    with sync_engine.connect() as conn:
        for stmt in migrations:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                # Column already exists or table doesn't exist yet — both are fine
                conn.rollback()


def init_db_sync():
    """Synchronous, rock-solid schema creation + safe migrations."""
    import app.models.budget  # noqa: register models
    sync_url = settings.DATABASE_URL_SYNC
    if sync_url.startswith("sqlite"):
        sync_engine = create_engine(sync_url, echo=False)
    else:
        sync_engine = create_engine(sync_url, echo=False, pool_pre_ping=True)

    # Create all tables (new deployments)
    Base.metadata.create_all(sync_engine)

    # Additive column migrations (existing deployments)
    _run_migrations(sync_engine)

    sync_engine.dispose()


async def init_db():
    init_db_sync()


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
