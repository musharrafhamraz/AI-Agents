"""Configuration management for Validata platform"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Validata"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str
    database_pool_size: int = 20
    
    # Redis
    redis_url: str
    
    # Vector Database (Pinecone)
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "validata-memory"
    
    # OpenAI
    openai_api_key: str
    openai_org_id: Optional[str] = None
    
    # Anthropic (optional)
    anthropic_api_key: Optional[str] = None
    
    # JWT Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # MCP Servers
    mcp_survey_port: int = 5001
    mcp_memory_port: int = 5002
    mcp_validation_port: int = 5003
    mcp_analytics_port: int = 5004
    
    # Celery
    celery_broker_url: str
    celery_result_backend: str
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/validata.log"
    
    def validate_required_fields(self) -> None:
        """Validate that all required configuration fields are present"""
        required_fields = [
            "database_url",
            "redis_url",
            "pinecone_api_key",
            "pinecone_environment",
            "openai_api_key",
            "secret_key",
            "celery_broker_url",
            "celery_result_backend"
        ]
        
        missing_fields = []
        for field in required_fields:
            value = getattr(self, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field.upper())
        
        if missing_fields:
            raise ValueError(
                f"Missing required configuration parameters: {', '.join(missing_fields)}. "
                f"Please check your .env file or environment variables."
            )


# Global settings instance
settings = Settings()

# Validate configuration on import
try:
    settings.validate_required_fields()
except ValueError as e:
    # Fail fast with descriptive error message
    raise RuntimeError(f"Configuration validation failed: {e}") from e
