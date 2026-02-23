"""
Tests for security utilities: password hashing and JWT operations.
Following TDD: Red-Green-Refactor
"""

import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError


class TestPasswordHashing:
    """Tests for bcrypt password hashing functions."""

    def test_hash_password_returns_string(self):
        """RED: Test that hash_password returns a string."""
        from backend.core.security import hash_password

        password = "testpassword123"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_hashes_for_same_password(self):
        """RED: Test that hashing same password twice produces different hashes (bcrypt salt)."""
        from backend.core.security import hash_password

        password = "testpassword123"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)

        assert hashed1 != hashed2

    def test_verify_password_correct_password(self):
        """RED: Test that verify_password returns True for correct password."""
        from backend.core.security import hash_password, verify_password

        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """RED: Test that verify_password returns False for incorrect password."""
        from backend.core.security import hash_password, verify_password

        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


class TestJWTOperations:
    """Tests for JWT token creation and decoding."""

    def test_create_access_token_returns_string(self):
        """RED: Test that create_access_token returns a string token."""
        from backend.core.security import create_access_token

        data = {"sub": "1"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_expected_data(self):
        """RED: Test that created token contains the expected payload data."""
        from backend.core.security import create_access_token, decode_access_token

        data = {"sub": "1", "username": "testuser"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "1"
        assert decoded["username"] == "testuser"

    def test_create_access_token_has_expiration(self):
        """RED: Test that created token includes expiration claim."""
        from backend.core.security import create_access_token, decode_access_token

        data = {"sub": "1"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert "exp" in decoded

    def test_create_access_token_custom_expiration(self):
        """RED: Test that custom expiration delta is respected."""
        from backend.core.security import create_access_token, decode_access_token

        data = {"sub": "1"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert "exp" in decoded

        exp_timestamp = decoded["exp"]
        now_timestamp = datetime.now(timezone.utc).timestamp()

        assert exp_timestamp > now_timestamp
        assert exp_timestamp < now_timestamp + 7200  # Less than 2 hours

    def test_decode_access_token_invalid_token(self):
        """RED: Test that decoding an invalid token returns None."""
        from backend.core.security import decode_access_token

        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)

        assert decoded is None

    def test_decode_access_token_expired_token(self):
        """RED: Test that decoding an expired token returns None."""
        from backend.core.security import create_access_token, decode_access_token

        data = {"sub": "1"}
        expires_delta = timedelta(minutes=-1)  # Already expired
        token = create_access_token(data, expires_delta=expires_delta)
        decoded = decode_access_token(token)

        assert decoded is None

    def test_decode_access_token_malformed_token(self):
        """RED: Test that decoding a malformed token returns None."""
        from backend.core.security import decode_access_token

        malformed_token = "not.a.valid.jwt"
        decoded = decode_access_token(malformed_token)

        assert decoded is None
