"""
Tests for database configuration and session management.
Following TDD: Red-Green-Refactor
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class TestDatabaseEngine:
    """Tests for async database engine creation."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        """Import engine fresh for each test."""
        from backend.core.database import engine
        self.engine = engine
        yield
        await engine.dispose()

    @pytest.mark.asyncio
    async def test_engine_is_async(self):
        """RED: Test that engine is an async engine."""
        assert isinstance(self.engine, AsyncEngine)

    @pytest.mark.asyncio
    async def test_engine_can_connect(self):
        """RED: Test that engine can connect to database."""
        from sqlalchemy import text

        async with self.engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.scalar()
            assert row == 1


class TestDatabaseSession:
    """Tests for async database session."""

    @pytest.mark.asyncio
    async def test_get_db_yields_async_session(self):
        """RED: Test that get_db yields an AsyncSession."""
        from backend.core.database import get_db

        session_generator = get_db()
        session = await anext(session_generator)

        assert isinstance(session, AsyncSession)

        await session.close()

        # Clean up the generator
        try:
            await anext(session_generator)
        except StopAsyncIteration:
            pass


class TestDatabaseInitialization:
    """Tests for database initialization."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        """Import init_db fresh for each test."""
        from backend.core.database import init_db, engine
        self.init_db = init_db
        self.engine = engine
        yield
        await engine.dispose()

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """RED: Test that init_db creates all tables."""
        from sqlalchemy import text

        await self.init_db()

        # Check that tables exist
        async with self.engine.connect() as conn:
            tables_result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in tables_result.fetchall()]
            assert "users" in tables

    @pytest.mark.asyncio
    async def test_init_db_idempotent(self):
        """RED: Test that init_db can be called multiple times without error."""
        # Should not raise any errors
        await self.init_db()
        await self.init_db()
