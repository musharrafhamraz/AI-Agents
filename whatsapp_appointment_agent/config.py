"""
Configuration management for WhatsApp Agent
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # WhatsApp Cloud API
    whatsapp_api_token: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str = "whatsapp_verify_token_123"
    
    # LLM Configuration
    gemini_api_key: str
    model_name: str = "gemini-2.0-flash-exp"
    
    # Database
    database_url: str = "sqlite:///./appointments.db"
    
    # Business Configuration
    business_name: str = "My Business"
    business_hours_start: int = 9  # 9 AM
    business_hours_end: int = 18   # 6 PM
    slot_duration_minutes: int = 60
    
    # Admin notifications
    admin_phone_number: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
