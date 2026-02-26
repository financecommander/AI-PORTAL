"""Backend configuration settings."""

import os
import sys
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Database
    database_url: str = Field(
        default="sqlite:///./ai_portal.db",
        description="Database connection URL"
    )
    
    # JWT Authentication
    jwt_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT token signing (MUST be changed in production)"
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    xai_api_key: str = Field(default="", env="XAI_API_KEY")
    courtlistener_api_key: str = Field(default="", env="COURTLISTENER_API_KEY")
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8501",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v: str, info) -> str:
        """Ensure JWT secret is changed in production."""
        if not info.data.get('debug', False):
            # In production mode (debug=False)
            if v == "dev-secret-key-change-in-production" or len(v) < 32:
                print(
                    "\n" + "="*70,
                    "\n🚨 SECURITY ERROR: Invalid JWT_SECRET_KEY",
                    "\n" + "="*70,
                    "\nThe JWT secret key must be changed in production!",
                    "\nGenerate a secure key with:",
                    "\n  python -c 'import secrets; print(secrets.token_urlsafe(32))'",
                    "\nThen set it in your .env file:",
                    "\n  JWT_SECRET_KEY=<your-secure-key>",
                    "\n" + "="*70 + "\n",
                    file=sys.stderr
                )
                sys.exit(1)
        return v
    
    @field_validator('openai_api_key', 'anthropic_api_key')
    @classmethod
    def validate_api_keys(cls, v: str, info) -> str:
        """Warn if critical API keys are missing in production."""
        if not info.data.get('debug', False) and not v:
            field_name = info.field_name
            print(
                f"⚠️  WARNING: {field_name.upper()} not set. "
                f"Some features may not work.",
                file=sys.stderr
            )
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
