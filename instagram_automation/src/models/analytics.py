"""Analytics data models."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PostMetrics(BaseModel):
    """Metrics for a single post."""
    post_id: str
    instagram_post_id: Optional[str] = None
    
    # Engagement metrics
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    
    # Reach metrics
    reach: int = 0
    impressions: int = 0
    
    # Calculated metrics
    engagement_rate: float = 0.0
    save_rate: float = 0.0
    
    # Timestamp
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AccountMetrics(BaseModel):
    """Account-level metrics."""
    account_id: str
    
    # Follower metrics
    followers_count: int = 0
    following_count: int = 0
    follower_growth: int = 0
    
    # Content metrics
    total_posts: int = 0
    avg_engagement_rate: float = 0.0
    avg_reach: int = 0
    
    # Time period
    period_start: datetime
    period_end: datetime
    
    # Timestamp
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PerformanceInsight(BaseModel):
    """Performance insights and recommendations."""
    insight_type: str  # "best_time", "top_hashtag", "content_type", etc.
    title: str
    description: str
    data: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 0.0
    
    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
