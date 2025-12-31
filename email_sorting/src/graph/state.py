"""LangGraph state schema for email processing workflow"""

from typing import TypedDict, List, Optional, Annotated, Dict, Any
from operator import add
from datetime import datetime


def merge_errors(existing: Optional[str], new: Optional[str]) -> Optional[str]:
    """Merge two error messages"""
    if not existing:
        return new
    if not new:
        return existing
    return f"{existing}; {new}"


class EmailState(TypedDict):
    """
    State schema that flows through the LangGraph workflow.
    Each agent reads from and writes to this shared state.
    """
    
    # ===== Email Data =====
    message_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    body_html: Optional[str]
    received_at: str
    thread_id: Optional[str]
    has_attachments: bool
    attachment_count: int
    
    # ===== Processing Results =====
    # Classification
    classification: Optional[str]
    classification_confidence: Optional[float]
    classification_reasoning: Optional[str]
    
    # Priority
    priority_score: Optional[float]
    urgency_level: Optional[str]  # Low, Medium, High
    recommended_response_time: Optional[str]
    priority_reasoning: Optional[str]
    
    # Intent
    intent: Optional[str]
    intent_confidence: Optional[float]
    action_items: Annotated[List[str], add]  # Accumulate action items
    requires_response: Optional[bool]
    intent_reasoning: Optional[str]
    
    # ===== Actions & Routing =====
    actions: Annotated[List[str], add]  # Accumulate actions to take
    labels: Annotated[List[str], add]   # Accumulate labels to apply
    
    # ===== Workflow Control =====
    processing_stage: str  # Current stage in workflow
    requires_human_review: bool
    overall_confidence: Optional[float]  # Aggregated confidence
    
    # ===== Context & Memory =====
    sender_history: Optional[Dict[str, Any]]  # Sender reputation data
    similar_emails: Optional[List[Dict[str, Any]]]  # From vector search
    
    # ===== Error Handling =====
    error: Annotated[Optional[str], merge_errors]
    retry_count: int
    
    # ===== Metadata =====
    processed_at: Optional[str]
    processing_time_ms: Optional[float]


class AgentOutput(TypedDict):
    """Standard output format for agents"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    confidence: Optional[float]
