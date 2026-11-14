from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base

# Async engine for FastAPI endpoints
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
else:
    engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=20, max_overflow=10)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def init_db_sync():
    """Synchronous, rock-solid schema creation."""
    import app.models.budget  # noqa: register models
    sync_url = settings.DATABASE_URL_SYNC
    if sync_url.startswith("sqlite"):
        sync_engine = create_engine(sync_url, echo=False)
    else:
        sync_engine = create_engine(sync_url, echo=False, pool_pre_ping=True)
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

async def init_db():
    init_db_sync()

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
