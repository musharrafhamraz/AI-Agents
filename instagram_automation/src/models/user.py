"""User and account models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class InstagramAccount(BaseModel):
    """Instagram account information."""
    id: str
    username: str
    name: Optional[str] = None
    biography: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    # Metrics
    followers_count: int = 0
    following_count: int = 0
    media_count: int = 0
    
    # Account type
    account_type: str = "BUSINESS"  # BUSINESS, CREATOR, PERSONAL
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserPreferences(BaseModel):
    """User preferences for content generation."""
    brand_name: str
    brand_voice: str = "professional and friendly"
    target_audience: str = "young professionals"
    
    # Content preferences
    preferred_themes: list[str] = Field(default_factory=list)
    excluded_topics: list[str] = Field(default_factory=list)
    
    # Posting preferences
    posting_frequency: int = 3  # posts per day
    preferred_posting_times: list[str] = Field(default_factory=lambda: ["09:00", "13:00", "18:00"])
    
    # Hashtag preferences
    default_hashtags: list[str] = Field(default_factory=list)
    hashtag_count: int = 15
    
    # Safety settings
    enable_human_review: bool = True
    auto_publish: bool = False
