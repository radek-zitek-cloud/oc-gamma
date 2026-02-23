"""
Tests for authentication service.
Following TDD: Red-Green-Refactor
"""

import pytest
import pytest_asyncio


class TestAuthenticateUser:
    """Tests for authenticate_user function."""

    @pytest_asyncio.fixture
    async def user_repo(self, db_session):
        """Create a UserRepository instance."""
        from backend.repositories.user import UserRepository

        return UserRepository(db_session)

    @pytest_asyncio.fixture
    async def test_user(self, user_repo):
        """Create a test user."""
        return await user_repo.create_user({
            "email": "auth@example.com",
            "username": "authuser",
            "password": "correctpassword",
        })

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session, test_user):
        """RED: Test successful authentication."""
        from backend.services.auth_service import authenticate_user

        user = await authenticate_user(db_session, "authuser", "correctpassword")

        assert user is not None
        assert user.username == "authuser"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session, test_user):
        """RED: Test authentication with wrong password."""
        from backend.services.auth_service import authenticate_user

        user = await authenticate_user(db_session, "authuser", "wrongpassword")

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, db_session):
        """RED: Test authentication with non-existent user."""
        from backend.services.auth_service import authenticate_user

        user = await authenticate_user(db_session, "nonexistent", "password")

        assert user is None


class TestRegisterUser:
    """Tests for register_user function."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, db_session):
        """RED: Test successful user registration."""
        from backend.services.auth_service import register_user
        from backend.schemas.user import UserCreate

        user_data = UserCreate(
            email="new@example.com",
            username="newuser",
            password="newpassword123",
            full_name="New User"
        )

        user = await register_user(db_session, user_data)

        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        assert user.full_name == "New User"

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, db_session):
        """RED: Test registration with duplicate email."""
        from backend.services.auth_service import register_user
        from backend.schemas.user import UserCreate

        # Create first user
        await register_user(db_session, UserCreate(
            email="dup@example.com",
            username="user1",
            password="password123"
        ))

        # Try to create second user with same email
        with pytest.raises(ValueError, match="Email already registered"):
            await register_user(db_session, UserCreate(
                email="dup@example.com",
                username="user2",
                password="password123"
            ))

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, db_session):
        """RED: Test registration with duplicate username."""
        from backend.services.auth_service import register_user
        from backend.schemas.user import UserCreate

        # Create first user
        await register_user(db_session, UserCreate(
            email="user1@example.com",
            username="dupuser",
            password="password123"
        ))

        # Try to create second user with same username
        with pytest.raises(ValueError, match="Username already taken"):
            await register_user(db_session, UserCreate(
                email="user2@example.com",
                username="dupuser",
                password="password123"
            ))


class TestGetCurrentUser:
    """Tests for get_current_user function."""

    @pytest_asyncio.fixture
    async def test_user(self, db_session):
        """Create a test user."""
        from backend.repositories.user import UserRepository

        repo = UserRepository(db_session)
        return await repo.create_user({
            "email": "current@example.com",
            "username": "currentuser",
            "password": "password123",
        })

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, db_session, test_user):
        """RED: Test getting current user with valid token."""
        from backend.services.auth_service import get_current_user
        from backend.core.security import create_access_token

        token = create_access_token({"sub": str(test_user.id)})
        user = await get_current_user(db_session, token)

        assert user is not None
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db_session):
        """RED: Test getting current user with invalid token."""
        from backend.services.auth_service import get_current_user

        with pytest.raises(ValueError, match="Invalid token"):
            await get_current_user(db_session, "invalid.token.here")

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self, db_session):
        """RED: Test getting current user when user doesn't exist."""
        from backend.services.auth_service import get_current_user
        from backend.core.security import create_access_token

        token = create_access_token({"sub": "99999"})

        with pytest.raises(ValueError, match="User not found"):
            await get_current_user(db_session, token)

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self, db_session):
        """RED: Test getting current user when user is inactive."""
        from backend.services.auth_service import get_current_user
        from backend.repositories.user import UserRepository
        from backend.core.security import create_access_token

        # Create inactive user
        repo = UserRepository(db_session)
        user = await repo.create_user({
            "email": "inactive@example.com",
            "username": "inactiveuser",
            "password": "password123",
        })
        user.is_active = False
        await db_session.flush()

        token = create_access_token({"sub": str(user.id)})

        with pytest.raises(ValueError, match="User is inactive"):
            await get_current_user(db_session, token)
