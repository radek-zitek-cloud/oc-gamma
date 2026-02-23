"""
User repository with user-specific data access operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import hash_password
from backend.models.user import User
from backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize the user repository."""
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get a user by username."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict) -> User:
        """
        Create a new user with hashed password.

        Args:
            user_data: Dictionary containing user data including 'password'.

        Returns:
            The created User instance.
        """
        # Hash the password before storing
        if "password" in user_data:
            plain_password = user_data.pop("password")
            user_data["hashed_password"] = hash_password(plain_password)

        return await self.create(user_data)

    async def update_user(self, user: User, update_data: dict) -> User:
        """
        Update user profile fields.

        Args:
            user: The user to update.
            update_data: Dictionary of fields to update.

        Returns:
            The updated User instance.
        """
        # Remove password if present (use change_password instead)
        update_data = {k: v for k, v in update_data.items() if k != "password"}
        return await self.update(user, update_data)

    async def change_password(self, user: User, new_hashed: str) -> User:
        """
        Change a user's password.

        Args:
            user: The user whose password to change.
            new_hashed: The new hashed password.

        Returns:
            The updated User instance.
        """
        return await self.update(user, {"hashed_password": new_hashed})
