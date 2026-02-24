"""
Tests for theme preference functionality.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def logged_in_client(client: AsyncClient):
    """Create a client with a logged-in user."""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "theme@example.com",
            "username": "themeuser",
            "password": "themepass123"
        }
    )
    # Login
    await client.post(
        "/api/v1/auth/login",
        data={"username": "themeuser", "password": "themepass123"}
    )
    return client


@pytest.mark.asyncio
async def test_get_me_includes_theme_preference(logged_in_client: AsyncClient):
    """Test that GET /me returns theme_preference field."""
    response = await logged_in_client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert "theme_preference" in data
    assert data["theme_preference"] in ["light", "dark", "system"]


@pytest.mark.asyncio
async def test_patch_theme_preference_success(logged_in_client: AsyncClient):
    """Test that PATCH /me/theme updates theme preference."""
    response = await logged_in_client.patch(
        "/api/v1/auth/me/theme",
        json={"theme_preference": "dark"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["theme_preference"] == "dark"


@pytest.mark.asyncio
async def test_patch_theme_preference_light(logged_in_client: AsyncClient):
    """Test updating theme preference to light."""
    response = await logged_in_client.patch(
        "/api/v1/auth/me/theme",
        json={"theme_preference": "light"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["theme_preference"] == "light"


@pytest.mark.asyncio
async def test_patch_theme_preference_system(logged_in_client: AsyncClient):
    """Test updating theme preference to system."""
    response = await logged_in_client.patch(
        "/api/v1/auth/me/theme",
        json={"theme_preference": "system"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["theme_preference"] == "system"


@pytest.mark.asyncio
async def test_patch_theme_preference_invalid_value(logged_in_client: AsyncClient):
    """Test that invalid theme value returns 422."""
    response = await logged_in_client.patch(
        "/api/v1/auth/me/theme",
        json={"theme_preference": "invalid_theme"},
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_theme_preference_unauthenticated(client: AsyncClient):
    """Test that unauthenticated request returns 401."""
    response = await client.patch(
        "/api/v1/auth/me/theme",
        json={"theme_preference": "dark"},
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_theme_preference_persists_after_update(logged_in_client: AsyncClient):
    """Test that theme preference persists after being updated."""
    # First update to dark
    await logged_in_client.patch(
        "/api/v1/auth/me/theme",
        json={"theme_preference": "dark"},
    )
    
    # Then verify it's persisted via GET /me
    response = await logged_in_client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["theme_preference"] == "dark"


@pytest.mark.asyncio
async def test_patch_theme_preference_rate_limit(logged_in_client: AsyncClient):
    """Test that theme updates are rate limited (10 requests per minute)."""
    # Note: Previous requests (login, other tests) may have already consumed some rate limit quota
    # So we make requests until we hit the limit
    
    request_count = 0
    while request_count < 15:  # Max attempts to hit rate limit
        response = await logged_in_client.patch(
            "/api/v1/auth/me/theme",
            json={"theme_preference": "dark" if request_count % 2 == 0 else "light"},
        )
        
        if response.status_code == 429:
            # Successfully hit rate limit
            assert "Rate limit exceeded" in response.json()["detail"]
            return
        
        assert response.status_code == 200
        request_count += 1
    
    # Should have hit rate limit before reaching max attempts
    pytest.fail("Rate limit was not triggered after 15 requests")
