"""Backend configuration settings."""

import os
from pydantic_settings import BaseSettings
from pydantic import Field


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
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    xai_api_key: str = Field(default="", env="XAI_API_KEY")
    courtlistener_api_key: str = Field(default="", env="COURTLISTENER_API_KEY")
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
