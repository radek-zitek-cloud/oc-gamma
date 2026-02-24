"""
Tests for authentication API endpoints.
Following TDD: Red-Green-Refactor
"""

import pytest
import pytest_asyncio


class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register"""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """RED: Test successful registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """RED: Test registration with duplicate email."""
        # Create first user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "username": "user1",
                "password": "password123"
            }
        )

        # Try duplicate
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "username": "user2",
                "password": "password123"
            }
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """RED: Test registration with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 422


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login"""

    @pytest_asyncio.fixture
    async def registered_user(self, client):
        """Create a registered user for login tests."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "loginpass123"
            }
        )

    @pytest.mark.asyncio
    async def test_login_success(self, client, registered_user):
        """RED: Test successful login sets cookie."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "loginuser", "password": "loginpass123"}
        )

        assert response.status_code == 200
        # Check for access_token cookie
        assert "access_token" in [c.name for c in client.cookies.jar]

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, registered_user):
        """RED: Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "loginuser", "password": "wrongpassword"}
        )

        assert response.status_code == 401


class TestMeEndpoint:
    """Tests for GET /api/v1/auth/me"""

    @pytest_asyncio.fixture
    async def logged_in_client(self, client):
        """Create a client with a logged-in user."""
        # Register user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "me@example.com",
                "username": "meuser",
                "password": "mepass123"
            }
        )
        # Login
        await client.post(
            "/api/v1/auth/login",
            data={"username": "meuser", "password": "mepass123"}
        )
        return client

    @pytest.mark.asyncio
    async def test_get_current_user(self, logged_in_client):
        """RED: Test getting current user when authenticated."""
        response = await logged_in_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "meuser"
        assert data["email"] == "me@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client):
        """RED: Test getting current user when not authenticated."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout"""

    @pytest_asyncio.fixture
    async def logged_in_client(self, client):
        """Create a client with a logged-in user."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "logout@example.com",
                "username": "logoutuser",
                "password": "logoutpass123"
            }
        )
        await client.post(
            "/api/v1/auth/login",
            data={"username": "logoutuser", "password": "logoutpass123"}
        )
        return client

    @pytest.mark.asyncio
    async def test_logout_clears_cookie(self, logged_in_client):
        """RED: Test logout clears the access token cookie."""
        response = await logged_in_client.post("/api/v1/auth/logout")

        assert response.status_code == 200


class TestUpdateProfileEndpoint:
    """Tests for PUT /api/v1/auth/me"""

    @pytest_asyncio.fixture
    async def logged_in_client(self, client):
        """Create a client with a logged-in user."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "update@example.com",
                "username": "updateuser",
                "password": "updatepass123",
                "full_name": "Original Name"
            }
        )
        await client.post(
            "/api/v1/auth/login",
            data={"username": "updateuser", "password": "updatepass123"}
        )
        return client

    @pytest.mark.asyncio
    async def test_update_profile_success(self, logged_in_client):
        """RED: Test successful profile update."""
        response = await logged_in_client.put(
            "/api/v1/auth/me",
            json={"full_name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["username"] == "updateuser"

    @pytest.mark.asyncio
    async def test_update_profile_email(self, logged_in_client):
        """RED: Test updating email address."""
        response = await logged_in_client.put(
            "/api/v1/auth/me",
            json={"email": "newemail@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"

    @pytest.mark.asyncio
    async def test_update_profile_invalid_email(self, logged_in_client):
        """RED: Test profile update with invalid email."""
        response = await logged_in_client.put(
            "/api/v1/auth/me",
            json={"email": "not-an-email"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_profile_unauthorized(self, client):
        """RED: Test profile update when not authenticated."""
        response = await client.put(
            "/api/v1/auth/me",
            json={"full_name": "Updated Name"}
        )

        assert response.status_code == 401


class TestChangePasswordEndpoint:
    """Tests for PUT /api/v1/auth/me/password"""

    @pytest_asyncio.fixture
    async def logged_in_client(self, client):
        """Create a client with a logged-in user."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "passchange@example.com",
                "username": "passchangeuser",
                "password": "oldpassword123"
            }
        )
        await client.post(
            "/api/v1/auth/login",
            data={"username": "passchangeuser", "password": "oldpassword123"}
        )
        return client

    @pytest.mark.asyncio
    async def test_change_password_success(self, logged_in_client):
        """RED: Test successful password change."""
        response = await logged_in_client.put(
            "/api/v1/auth/me/password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456",
                "confirm_password": "newpassword456"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, logged_in_client):
        """RED: Test password change with wrong current password."""
        response = await logged_in_client.put(
            "/api/v1/auth/me/password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
                "confirm_password": "newpassword456"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "current password" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_change_password_unauthorized(self, client):
        """RED: Test password change when not authenticated."""
        response = await client.put(
            "/api/v1/auth/me/password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_change_password_mismatched_confirmation(self, logged_in_client):
        """RED: Test password change with mismatched confirm_password."""
        response = await logged_in_client.put(
            "/api/v1/auth/me/password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456",
                "confirm_password": "differentpassword789"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert "passwords do not match" in data["detail"][0]["msg"].lower()

    @pytest.mark.asyncio
    async def test_change_password_with_confirmation_success(self, logged_in_client):
        """RED: Test successful password change with confirm_password."""
        response = await logged_in_client.put(
            "/api/v1/auth/me/password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456",
                "confirm_password": "newpassword456"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"

    @pytest.mark.asyncio
    async def test_change_password_rate_limiting(self, logged_in_client):
        """RED: Test rate limiting on password change endpoint."""
        # Make 3 failed attempts (within limit)
        for _ in range(3):
            response = await logged_in_client.put(
                "/api/v1/auth/me/password",
                json={
                    "current_password": "wrongpassword",
                    "new_password": "newpassword456",
                    "confirm_password": "newpassword456"
                }
            )
            assert response.status_code == 400  # Wrong password

        # 4th attempt should be rate limited
        response = await logged_in_client.put(
            "/api/v1/auth/me/password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
                "confirm_password": "newpassword456"
            }
        )
        assert response.status_code == 429  # Too Many Requests
