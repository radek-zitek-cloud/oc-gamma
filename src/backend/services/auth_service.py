"""
Authentication service with cross-repository business logic.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import decode_access_token, verify_password
from backend.models.user import User
from backend.repositories.user import UserRepository
from backend.schemas.user import UserCreate


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    """
    Authenticate a user by username and password.

    Args:
        db: The database session.
        username: The username to authenticate.
        password: The plain text password to verify.

    Returns:
        The User if authentication succeeds, None otherwise.
    """
    repo = UserRepository(db)
    user = await repo.get_by_username(username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Register a new user.

    Args:
        db: The database session.
        user_data: The user creation data.

    Returns:
        The created User.

    Raises:
        ValueError: If email or username is already taken.
    """
    repo = UserRepository(db)

    # Check for duplicate email
    existing_email = await repo.get_by_email(user_data.email)
    if existing_email:
        raise ValueError("Email already registered")

    # Check for duplicate username
    existing_username = await repo.get_by_username(user_data.username)
    if existing_username:
        raise ValueError("Username already taken")

    # Create the user
    user_dict = user_data.model_dump()
    return await repo.create_user(user_dict)


async def get_current_user(db: AsyncSession, token: str) -> User:
    """
    Get the current user from a JWT token.

    Args:
        db: The database session.
        token: The JWT access token.

    Returns:
        The authenticated User.

    Raises:
        ValueError: If token is invalid or user not found/inactive.
    """
    payload = decode_access_token(token)

    if not payload:
        raise ValueError("Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid token")

    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User is inactive")

    return user
