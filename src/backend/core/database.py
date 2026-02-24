"""
Database configuration and session management.
Uses SQLAlchemy 2.0 async patterns.
"""

from collections.abc import AsyncGenerator

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Yields:
        AsyncSession: Database session for request handling.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def run_migrations() -> None:
    """
    Run database migrations using Alembic.
    This is a synchronous wrapper that runs in a thread pool.
    """
    import os
    
    try:
        # Load alembic configuration
        # Look for alembic.ini in the current directory and backend directory
        alembic_ini_paths = [
            "alembic.ini",
            os.path.join(os.path.dirname(__file__), "..", "alembic.ini"),
        ]
        
        alembic_cfg = None
        for path in alembic_ini_paths:
            if os.path.exists(path):
                alembic_cfg = Config(path)
                break
        
        if alembic_cfg is None:
            raise FileNotFoundError("alembic.ini not found in expected locations")
        
        # Run migrations to latest revision
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise


async def init_db() -> None:
    """
    Initialize database by creating tables and running Alembic migrations.
    """
    # Import models to register them with Base metadata
    from backend.models import User  # noqa: F401
    from backend.models.base import Base
    
    # Create all tables first (for fresh databases)
    # This ensures the schema exists before running migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Import and run async migrations
    from backend.core.migrations import run_migrations_async
    
    await run_migrations_async()
    logger.info("Database migrations completed successfully")
