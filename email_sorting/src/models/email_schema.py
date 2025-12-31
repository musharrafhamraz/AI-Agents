"""Pydantic models for email data structures"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class EmailMetadata(BaseModel):
    """Email metadata extracted from headers"""
    message_id: str
    sender: EmailStr
    recipient: EmailStr
    subject: str
    received_at: datetime
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    has_attachments: bool = False
    attachment_count: int = 0
    labels: List[str] = Field(default_factory=list)


class EmailContent(BaseModel):
    """Parsed email content"""
    body_text: str
    body_html: Optional[str] = None
    signature: Optional[str] = None
    quoted_text: Optional[str] = None
    main_content: str  # Body without signature/quotes


class EmailEntity(BaseModel):
    """Entities extracted from email"""
    people: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)


class Email(BaseModel):
    """Complete email representation"""
    metadata: EmailMetadata
    content: EmailContent
    entities: Optional[EmailEntity] = None
    raw_data: Optional[Dict[str, Any]] = None


class ClassificationResult(BaseModel):
    """Result from classification agent"""
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class PriorityResult(BaseModel):
    """Result from priority scoring agent"""
    priority_score: float = Field(ge=0.0, le=10.0)
    urgency_level: str  # Low, Medium, High
    recommended_response_time: str
    reasoning: str


class IntentResult(BaseModel):
    """Result from intent detection agent"""
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    action_items: List[str] = Field(default_factory=list)
    requires_response: bool
    reasoning: str


class RouterDecision(BaseModel):
    """Decision from router agent"""
    actions: List[str]
    reasoning: str


class SenderProfile(BaseModel):
    """Sender reputation and history"""
    email: EmailStr
    total_emails: int = 0
    avg_priority: float = 0.0
    common_categories: List[str] = Field(default_factory=list)
    response_rate: float = 0.0
    is_vip: bool = False
    last_interaction: Optional[datetime] = None
