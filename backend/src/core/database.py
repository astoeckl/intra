"""
Database Configuration.

Provides async SQLAlchemy setup with connection pooling.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from src.core.config import get_settings

settings = get_settings()

# Async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.

    Handles transaction commit on success, rollback on exception.
    Sessions are automatically closed after request completes.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database schema.

    Creates all tables defined in SQLAlchemy models.
    Safe to call multiple times (uses CREATE IF NOT EXISTS).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
