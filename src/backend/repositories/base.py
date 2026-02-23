"""
Base repository with generic CRUD operations.
Uses SQLAlchemy 2.0 async syntax.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic base repository with standard CRUD operations."""

    def __init__(self, session: AsyncSession, model_class: type[T]):
        """
        Initialize the repository.

        Args:
            session: The async database session.
            model_class: The model class this repository manages.
        """
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, id: int) -> T | None:
        """Get a model instance by ID."""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Get all model instances with pagination."""
        result = await self.session.execute(
            select(self.model_class).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj_in: dict[str, Any]) -> T:
        """Create a new model instance."""
        db_obj = self.model_class(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: T, obj_in: dict[str, Any]) -> T:
        """Update a model instance."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """Delete a model instance by ID."""
        obj = await self.get_by_id(id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
            return True
        return False
