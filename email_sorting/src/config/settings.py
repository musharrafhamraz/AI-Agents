"""Configuration settings for the email sorting agent"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # LLM Configuration
    LLM_PROVIDER: str = "groq"  # openai, anthropic, groq
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    MODEL_NAME: str = "llama-3.1-8b-instant"  # or claude-3-5-sonnet-20241022, etc.
    
    # Email Provider
    EMAIL_PROVIDER: str = "gmail"  # gmail, outlook, imap
    
    # Gmail OAuth
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    
    # Outlook OAuth
    OUTLOOK_CLIENT_ID: str = ""
    OUTLOOK_CLIENT_SECRET: str = ""
    OUTLOOK_TENANT_ID: str = ""
    
    # IMAP Settings
    IMAP_SERVER: str = ""
    IMAP_PORT: int = 993
    IMAP_USERNAME: str = ""
    IMAP_PASSWORD: str = ""
    
    # Processing Settings
    BATCH_SIZE: int = 10
    CONFIDENCE_THRESHOLD: float = 0.8
    MAX_EMAILS_PER_RUN: int = 100
    
    # Categories
    CATEGORIES: List[str] = [
        "Work",
        "Personal", 
        "Promotions",
        "Social",
        "Transactional",
        "Spam"
    ]
    
    # Vector Store
    VECTOR_DB_PATH: str = "data/vector_db"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Database
    DATABASE_URL: str = "sqlite:///data/email_sorting.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/email_agent.log"
    
    # Feature Flags
    ENABLE_HUMAN_REVIEW: bool = True
    ENABLE_LEARNING: bool = True
    ENABLE_VECTOR_SEARCH: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
