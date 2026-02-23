"""
FastAPI dependency injection for authentication and database.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db as _get_db
from backend.core.security import decode_access_token
from backend.models.user import User
from backend.repositories.user import UserRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async for session in _get_db():
        yield session


async def get_user_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    """Dependency for getting UserRepository."""
    return UserRepository(db)


async def get_current_user_id(
    access_token: Annotated[str | None, Cookie()] = None,
) -> int:
    """
    Extract user ID from JWT cookie.

    Args:
        access_token: The JWT token from HttpOnly cookie.

    Returns:
        The user ID from the token.

    Raises:
        HTTPException: If token is missing or invalid.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(access_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(payload["sub"])


async def get_current_user(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> User:
    """
    Get the current authenticated user.

    Args:
        user_id: The user ID from token.
        repo: The user repository.

    Returns:
        The authenticated User instance.

    Raises:
        HTTPException: If user not found or inactive.
    """
    user = await repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Verify that the current user is active.

    Args:
        current_user: The current authenticated user.

    Returns:
        The user if active.

    Raises:
        HTTPException: If user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return current_user
