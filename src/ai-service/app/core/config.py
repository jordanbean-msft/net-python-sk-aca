"""Application configuration settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    # Azure AI Foundry settings
    azure_ai_project_endpoint: str
    azure_ai_model_deployment: str
    azure_openai_api_key: str | None = None

    # Application settings
    app_name: str = "AI Chat Service"
    log_level: str = "INFO"

    # CORS settings
    cors_origins: list[str] | str = ["*"]

    # Tracing settings
    enable_tracing: bool = True
    otlp_endpoint: str = "http://localhost:4318/v1/traces"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle comma-separated string or single value
            if "," in v:
                return [origin.strip() for origin in v.split(",")]
            # Handle JSON array string
            if v.startswith("["):
                import json
                return json.loads(v)
            # Single value
            return [v]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
