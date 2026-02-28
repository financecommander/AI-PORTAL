"""Tests for security fixes in backend configuration."""

import os
import sys
import pytest
from unittest.mock import patch


def test_jwt_secret_validation_rejects_default_in_production():
    """Test that default JWT secret is rejected when DEBUG=false."""
    # Clear any existing settings import
    if 'backend.config.settings' in sys.modules:
        del sys.modules['backend.config.settings']
    
    with patch.dict(os.environ, {
        'DEBUG': 'false',
        'JWT_SECRET_KEY': 'dev-secret-key-change-in-production'
    }):
        with pytest.raises(SystemExit) as exc_info:
            from backend.config.settings import settings
        assert exc_info.value.code == 1


def test_jwt_secret_validation_rejects_short_key_in_production():
    """Test that short JWT secret is rejected when DEBUG=false."""
    if 'backend.config.settings' in sys.modules:
        del sys.modules['backend.config.settings']
    
    with patch.dict(os.environ, {
        'DEBUG': 'false',
        'JWT_SECRET_KEY': 'short'
    }):
        with pytest.raises(SystemExit) as exc_info:
            from backend.config.settings import settings
        assert exc_info.value.code == 1


def test_jwt_secret_validation_accepts_valid_key_in_production():
    """Test that valid JWT secret is accepted when DEBUG=false."""
    if 'backend.config.settings' in sys.modules:
        del sys.modules['backend.config.settings']
    
    with patch.dict(os.environ, {
        'DEBUG': 'false',
        'JWT_SECRET_KEY': 'a' * 32  # Valid 32+ character key
    }):
        from backend.config.settings import settings
        assert settings.jwt_secret_key == 'a' * 32


def test_jwt_secret_validation_allows_default_in_debug_mode():
    """Test that default JWT secret is allowed when DEBUG=true."""
    if 'backend.config.settings' in sys.modules:
        del sys.modules['backend.config.settings']
    
    with patch.dict(os.environ, {
        'DEBUG': 'true',
        'JWT_SECRET_KEY': 'dev-secret-key-change-in-production'
    }):
        from backend.config.settings import settings
        assert settings.jwt_secret_key == 'dev-secret-key-change-in-production'


def test_cors_origins_configuration():
    """Test that CORS origins can be configured via environment."""
    if 'backend.config.settings' in sys.modules:
        del sys.modules['backend.config.settings']
    
    with patch.dict(os.environ, {
        'CORS_ORIGINS': 'https://app.example.com,https://api.example.com',
        'DEBUG': 'true',
        'JWT_SECRET_KEY': 'test-key-for-testing-only-min-32-chars'
    }):
        from backend.config.settings import settings
        assert settings.cors_origins == 'https://app.example.com,https://api.example.com'


def test_cors_origins_default_value():
    """Test that CORS origins have sensible defaults."""
    if 'backend.config.settings' in sys.modules:
        del sys.modules['backend.config.settings']
    
    with patch.dict(os.environ, {
        'DEBUG': 'true',
        'JWT_SECRET_KEY': 'test-key-for-testing-only-min-32-chars'
    }, clear=True):
        from backend.config.settings import settings
        assert 'localhost' in settings.cors_origins


def test_api_key_warning_in_production(capsys):
    """Test that missing API keys generate warnings in production."""
    if 'backend.config.settings' in sys.modules:
        del sys.modules['backend.config.settings']
    
    with patch.dict(os.environ, {
        'DEBUG': 'false',
        'JWT_SECRET_KEY': 'a' * 32,
        'OPENAI_API_KEY': '',
        'ANTHROPIC_API_KEY': ''
    }):
        from backend.config.settings import settings
        captured = capsys.readouterr()
        assert 'WARNING' in captured.err or 'OPENAI_API_KEY' in captured.err


def test_litellm_in_requirements():
    """Test that litellm IS in requirements (needed by CrewAI pipelines)."""
    requirements_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'requirements.txt'
    )
    with open(requirements_path, 'r') as f:
        requirements = f.read()
    assert 'litellm' in requirements.lower()
