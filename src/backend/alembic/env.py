"""
Alembic environment configuration for async SQLAlchemy.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import models to ensure they're registered with Base metadata
from backend.models.base import Base
from backend.models.user import User  # noqa: F401
from backend.core.config import settings

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        {"sqlalchemy.url": settings.DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


async def run_migrations_async() -> None:
    """
    Run migrations in async mode from within the application.
    Use this when calling from within an async context (e.g., FastAPI lifespan).
    """
    await run_async_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (CLI entry point)."""
    # Check if we're already in an async context
    try:
        loop = asyncio.get_running_loop()
        # We're in an async context, can't use asyncio.run
        raise RuntimeError(
            "Cannot run migrations synchronously from async context. "
            "Use run_migrations_async() instead."
        )
    except RuntimeError as e:
        if "no running event loop" in str(e):
            # No event loop running, safe to use asyncio.run()
            asyncio.run(run_async_migrations())
        else:
            raise


# This is the entry point when run from CLI
# The context.config is set by alembic when running from command line
# We check if it's available to avoid errors when importing this module directly
try:
    # When run from alembic CLI, context.config will be available
    alembic_config = context.config
    if alembic_config is not None and hasattr(alembic_config, 'config_file_name'):
        # Interpret the config file for Python logging
        if alembic_config.config_file_name is not None:
            fileConfig(alembic_config.config_file_name)
        
        if context.is_offline_mode():
            run_migrations_offline()
        else:
            run_migrations_online()
except (AttributeError, NameError):
    # context.config not available - we're being imported, not run by alembic
    # This is fine, the run_migrations_async() function can still be called
    pass
