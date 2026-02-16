"""
Tests for JWT handler.
"""
import pytest
from datetime import timedelta
from jose import jwt
from backend.auth.jwt_handler import create_access_token, verify_token
from backend.config.settings import settings
from backend.errors import AuthenticationError


class TestJWTHandler:
    """Tests for JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test creating a JWT access token."""
        data = {"sub": "test@financecommander.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token can be decoded
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "test@financecommander.com"
        assert "exp" in payload
    
    def test_create_access_token_with_expiration(self):
        """Test creating a token with custom expiration."""
        data = {"sub": "test@financecommander.com"}
        expires_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "test@financecommander.com"
    
    def test_verify_token_valid(self):
        """Test verifying a valid token."""
        data = {"sub": "test@financecommander.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "test@financecommander.com"
    
    def test_verify_token_invalid(self):
        """Test verifying an invalid token."""
        with pytest.raises(AuthenticationError) as exc_info:
            verify_token("invalid-token")
        
        assert "Invalid token" in str(exc_info.value)
    
    def test_verify_token_expired(self):
        """Test verifying an expired token."""
        data = {"sub": "test@financecommander.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(AuthenticationError):
            verify_token(token)
