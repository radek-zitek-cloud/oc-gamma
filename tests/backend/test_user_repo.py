"""
Tests for user repository operations.
Following TDD: Red-Green-Refactor
"""

import pytest
import pytest_asyncio


class TestUserRepository:
    """Tests for UserRepository operations."""

    @pytest_asyncio.fixture
    async def user_repo(self, db_session):
        """Create a UserRepository instance."""
        from backend.repositories.user import UserRepository

        return UserRepository(db_session)

    @pytest.mark.asyncio
    async def test_create_user(self, user_repo):
        """RED: Test creating a user."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        }

        user = await user_repo.create_user(user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password != "testpass123"  # Should be hashed
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_get_by_email(self, user_repo):
        """RED: Test getting user by email."""
        # Create a user first
        user_data = {
            "email": "find@example.com",
            "username": "finduser",
            "password": "testpass123",
        }
        created = await user_repo.create_user(user_data)

        # Find by email
        found = await user_repo.get_by_email("find@example.com")

        assert found is not None
        assert found.id == created.id
        assert found.email == "find@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, user_repo):
        """RED: Test getting user by email when not exists."""
        found = await user_repo.get_by_email("nonexistent@example.com")

        assert found is None

    @pytest.mark.asyncio
    async def test_get_by_username(self, user_repo):
        """RED: Test getting user by username."""
        # Create a user first
        user_data = {
            "email": "user@example.com",
            "username": "uniqueuser",
            "password": "testpass123",
        }
        created = await user_repo.create_user(user_data)

        # Find by username
        found = await user_repo.get_by_username("uniqueuser")

        assert found is not None
        assert found.id == created.id
        assert found.username == "uniqueuser"

    @pytest.mark.asyncio
    async def test_get_by_username_not_found(self, user_repo):
        """RED: Test getting user by username when not exists."""
        found = await user_repo.get_by_username("nonexistentuser")

        assert found is None

    @pytest.mark.asyncio
    async def test_update_user(self, user_repo):
        """RED: Test updating user profile."""
        # Create a user first
        user_data = {
            "email": "update@example.com",
            "username": "updateuser",
            "password": "testpass123",
        }
        user = await user_repo.create_user(user_data)

        # Update user
        updated = await user_repo.update_user(user, {"full_name": "Updated Name"})

        assert updated.full_name == "Updated Name"

    @pytest.mark.asyncio
    async def test_change_password(self, user_repo):
        """RED: Test changing user password."""
        # Create a user first
        user_data = {
            "email": "pass@example.com",
            "username": "passuser",
            "password": "oldpassword",
        }
        user = await user_repo.create_user(user_data)
        old_hash = user.hashed_password

        # Change password
        updated = await user_repo.change_password(user, "newhashedpassword123")

        assert updated.hashed_password != old_hash
        assert updated.hashed_password == "newhashedpassword123"
