"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    # Azure AI Foundry settings
    azure_ai_project_endpoint: str
    azure_ai_model_deployment: str

    # Application settings
    app_name: str = "AI Chat Service"
    log_level: str = "INFO"

    # CORS settings
    cors_origins: list[str] = ["*"]

    # Tracing settings
    enable_tracing: bool = True
    otlp_endpoint: str = "http://localhost:4318/v1/traces"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
