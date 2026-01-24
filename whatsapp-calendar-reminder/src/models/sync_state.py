"""Sync State model."""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin, generate_uuid


class SyncStatus(str, Enum):
    """Sync status enum."""

    SUCCESS = "success"
    FAILED = "failed"


class SyncState(Base, TimestampMixin):
    """Model for tracking calendar sync state."""

    __tablename__ = "sync_state"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    calendar_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    sync_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_sync_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_sync_status: Mapped[SyncStatus] = mapped_column(
        SQLEnum(SyncStatus),
        default=SyncStatus.SUCCESS,
        nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<SyncState(calendar_id={self.calendar_id}, status={self.last_sync_status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "calendar_id": self.calendar_id,
            "sync_token": self.sync_token,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "last_sync_status": self.last_sync_status.value,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
