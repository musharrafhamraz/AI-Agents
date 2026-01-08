"""Configuration settings for the Instagram Agent."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Google Gemini API
    google_api_key: str
    gemini_model: str = "gemini-1.5-pro"
    
    # Image Generation
    # Options: 'google' (Nano Banana) or 'pollinations' (Free)
    image_provider: str = "pollinations" 
    image_model: str = "gemini-2.5-flash-image"
    
    # Instagram Graph API
    instagram_access_token: str
    instagram_business_account_id: str
    facebook_page_id: str
    
    # Database
    database_url: str = "sqlite:///./instagram_agent.db"
    
    # Application Settings
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Content Settings
    brand_name: str = "Your Brand"
    brand_voice: str = "professional and friendly"
    target_audience: str = "young professionals aged 25-35"
    default_hashtag_count: int = 15
    
    # Scheduling
    timezone: str = "UTC"
    default_posting_times: str = "09:00,13:00,18:00"
    
    # Safety & Limits
    max_posts_per_day: int = 3
    enable_human_review: bool = True
    auto_publish: bool = False
    
    # Rate Limiting
    instagram_api_rate_limit: int = 200
    api_retry_attempts: int = 3
    api_retry_delay: int = 5
    
    @property
    def posting_times_list(self) -> List[str]:
        """Convert posting times string to list."""
        return [time.strip() for time in self.default_posting_times.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
