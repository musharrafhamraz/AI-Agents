"""Calendar Event model."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin, generate_uuid


class CalendarEvent(Base, TimestampMixin):
    """Model for storing Google Calendar events."""

    __tablename__ = "calendar_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    google_event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    calendar_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    attendees: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<CalendarEvent(id={self.id}, title={self.title}, start={self.start_time})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "google_event_id": self.google_event_id,
            "calendar_id": self.calendar_id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "location": self.location,
            "attendees": self.attendees,
            "reminder_enabled": self.reminder_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
