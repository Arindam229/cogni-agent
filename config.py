"""
Configuration management using Pydantic Settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    # Google AI Configuration
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    google_model: str = Field(default="gemini-2.5-flash", alias="GOOGLE_MODEL")
    google_fallback_models: str = Field(
        default="gemini-2.0-flash,gemini-1.5-flash,gemini-2.0-flash-lite",
        alias="GOOGLE_FALLBACK_MODELS",
    )
    llm_temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2000, alias="MAX_TOKENS")

    # CORS Configuration
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")

    # Application Settings
    app_name: str = Field(default="Cognizance AI Assistant", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def fallback_models_list(self) -> List[str]:
        """Parse fallback models from comma-separated string."""
        return [m.strip() for m in self.google_fallback_models.split(",") if m.strip()]


# Global settings instance
settings = Settings()
