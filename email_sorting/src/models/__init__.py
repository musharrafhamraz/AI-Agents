"""Models package"""

from .email_schema import (
    EmailMetadata,
    EmailContent,
    EmailEntity,
    Email,
    ClassificationResult,
    PriorityResult,
    IntentResult,
    RouterDecision,
    SenderProfile,
)

__all__ = [
    "EmailMetadata",
    "EmailContent",
    "EmailEntity",
    "Email",
    "ClassificationResult",
    "PriorityResult",
    "IntentResult",
    "RouterDecision",
    "SenderProfile",
]
