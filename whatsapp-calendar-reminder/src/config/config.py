"""Application configuration using Pydantic Settings."""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="WhatsApp Calendar Reminder", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    secret_key: str = Field(..., alias="SECRET_KEY")

    # Database
    database_url: str = Field(..., alias="DATABASE_URL")

    # Redis (optional for initial setup)
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Google Calendar API
    google_client_id: str = Field(..., alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(..., alias="GOOGLE_REDIRECT_URI")
    google_calendar_id: str = Field(default="primary", alias="GOOGLE_CALENDAR_ID")

    # WhatsApp Business API
    whatsapp_api_url: str = Field(
        default="https://graph.facebook.com/v18.0",
        alias="WHATSAPP_API_URL"
    )
    whatsapp_access_token: str = Field(..., alias="WHATSAPP_ACCESS_TOKEN")
    whatsapp_phone_number_id: str = Field(..., alias="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_business_account_id: str = Field(..., alias="WHATSAPP_BUSINESS_ACCOUNT_ID")

    # Reminder Settings
    default_reminder_hours: int = Field(default=24, alias="DEFAULT_REMINDER_HOURS")
    sync_interval_minutes: int = Field(default=15, alias="SYNC_INTERVAL_MINUTES")
    max_retry_attempts: int = Field(default=3, alias="MAX_RETRY_ATTEMPTS")

    # User Settings (for single-user setup)
    user_email: str = Field(..., alias="USER_EMAIL")
    user_phone_number: str = Field(..., alias="USER_PHONE_NUMBER")
    user_timezone: str = Field(default="UTC", alias="USER_TIMEZONE")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper

    @field_validator("default_reminder_hours")
    @classmethod
    def validate_reminder_hours(cls, v: int) -> int:
        """Validate reminder hours is positive."""
        if v <= 0:
            raise ValueError("Reminder hours must be positive")
        return v


# Global settings instance
settings = Settings()
