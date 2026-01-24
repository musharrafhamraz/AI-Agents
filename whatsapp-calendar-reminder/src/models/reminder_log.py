"""Reminder Log model."""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import String, DateTime, Integer, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin, generate_uuid


class MessageStatus(str, Enum):
    """Message delivery status enum."""

    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class ReminderLog(Base, TimestampMixin):
    """Model for logging reminder message delivery."""

    __tablename__ = "reminder_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    event_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("calendar_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[MessageStatus] = mapped_column(
        SQLEnum(MessageStatus),
        default=MessageStatus.SCHEDULED,
        nullable=False,
        index=True
    )
    scheduled_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    sent_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        """String representation."""
        return f"<ReminderLog(id={self.id}, event_id={self.event_id}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "phone_number": self.phone_number,
            "message_id": self.message_id,
            "template_name": self.template_name,
            "status": self.status.value,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "sent_time": self.sent_time.isoformat() if self.sent_time else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
