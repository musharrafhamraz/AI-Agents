"""State definitions for LangGraph workflows."""
from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langgraph.graph import add_messages
from datetime import datetime


def merge_errors(existing: List[str], new: List[str]) -> List[str]:
    """Custom reducer to merge error messages from parallel agents."""
    if existing is None:
        existing = []
    if new is None:
        new = []
    return existing + new


def merge_content_queue(existing: List[Dict], new: List[Dict]) -> List[Dict]:
    """Custom reducer to merge content queue items."""
    if existing is None:
        existing = []
    if new is None:
        new = []
    return existing + new


class InstagramState(TypedDict):
    """State for Instagram automation workflow."""
    
    # Content management
    content_queue: Annotated[List[Dict[str, Any]], merge_content_queue]
    current_post: Optional[Dict[str, Any]]
    
    # Scheduling
    scheduled_posts: List[Dict[str, Any]]
    next_post_time: Optional[str]
    
    # Analytics
    recent_metrics: Dict[str, Any]
    performance_trends: Dict[str, Any]
    
    # Engagement
    pending_comments: List[Dict[str, Any]]
    pending_dms: List[Dict[str, Any]]
    
    # User preferences
    user_preferences: Dict[str, Any]
    
    # Workflow control
    current_agent: str
    next_action: str
    task_description: Optional[str]
    
    # Error handling
    errors: Annotated[List[str], merge_errors]
    
    # Messages (for agent communication)
    messages: Annotated[list, add_messages]
    
    # Metadata
    workflow_start_time: Optional[datetime]
    last_updated: Optional[datetime]


class ContentCreationState(TypedDict):
    """State for content creation workflow."""
    
    # Input
    content_theme: Optional[str]
    target_audience: Optional[str]
    brand_voice: Optional[str]
    
    # Generated content
    caption: Optional[str]
    hashtags: List[str]
    image_prompt: Optional[str]
    image_url: Optional[str]
    
    # Workflow control
    current_step: str
    requires_review: bool
    approved: bool
    
    # Error handling
    errors: Annotated[List[str], merge_errors]
    
    # Messages
    messages: Annotated[list, add_messages]


class EngagementState(TypedDict):
    """State for engagement management workflow."""
    
    # Input
    comments_to_process: List[Dict[str, Any]]
    dms_to_process: List[Dict[str, Any]]
    
    # Processing
    current_comment: Optional[Dict[str, Any]]
    generated_reply: Optional[str]
    sentiment: Optional[str]
    
    # Output
    processed_comments: List[Dict[str, Any]]
    flagged_for_review: List[Dict[str, Any]]
    
    # Workflow control
    current_step: str
    
    # Error handling
    errors: Annotated[List[str], merge_errors]
    
    # Messages
    messages: Annotated[list, add_messages]
