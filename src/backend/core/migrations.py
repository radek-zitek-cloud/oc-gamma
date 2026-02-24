"""
Standalone database migration runner.
This runs migrations without using alembic's CLI context.
"""

import asyncio
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


async def run_migrations_async() -> None:
    """
    Run database migrations programmatically.
    This is a simplified migration system that checks and applies
    migrations in order without using alembic's CLI.
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
    )
    
    try:
        async with engine.connect() as conn:
            # Check if alembic_version table exists
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
            ))
            has_version_table = result.scalar() is not None
            
            if not has_version_table:
                # Create alembic_version table
                await conn.execute(text(
                    "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"
                ))
                await conn.execute(text(
                    "INSERT INTO alembic_version (version_num) VALUES ('base')"
                ))
                await conn.commit()
                logger.info("Created alembic_version table")
            
            # Get current version
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar() or 'base'
            logger.debug(f"Current database version: {current_version}")
            
            # Define migrations
            migrations = [
                ('001_add_theme_preference', add_theme_preference),
            ]
            
            # Run pending migrations
            for version, migration_func in migrations:
                if current_version == 'base' or version > current_version:
                    logger.info(f"Running migration: {version}")
                    await migration_func(conn)
                    
                    # Update version
                    await conn.execute(
                        text("UPDATE alembic_version SET version_num = :version"),
                        {"version": version}
                    )
                    await conn.commit()
                    logger.info(f"Migration {version} completed")
                else:
                    logger.debug(f"Migration {version} already applied")
            
            logger.info("All migrations completed successfully")
    finally:
        await engine.dispose()


async def add_theme_preference(conn) -> None:
    """
    Migration 001: Add theme_preference column to users table.
    """
    # Check if column already exists (for idempotency)
    result = await conn.execute(text(
        "SELECT name FROM pragma_table_info('users') WHERE name = 'theme_preference'"
    ))
    has_column = result.scalar() is not None
    
    if not has_column:
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN theme_preference VARCHAR(20) DEFAULT 'system' NOT NULL"
        ))
        logger.info("Added theme_preference column to users table")
    else:
        logger.debug("theme_preference column already exists")
