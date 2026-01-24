"""Reminder engine for calculating and scheduling reminders."""

from datetime import datetime, timedelta
from typing import Optional
import pytz
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models import CalendarEvent, ReminderLog, UserPreference
from src.models.reminder_log import MessageStatus
from src.config import settings


class ReminderEngine:
    """Engine for calculating reminder times and scheduling."""

    def __init__(self, db: Session):
        """
        Initialize reminder engine.
        
        Args:
            db: Database session
        """
        self.db = db

    def calculate_reminder_time(
        self,
        event_start: datetime,
        advance_hours: int = 24,
        user_timezone: str = "UTC"
    ) -> datetime:
        """
        Calculate when to send reminder.
        
        Args:
            event_start: Event start time
            advance_hours: Hours before event to send reminder
            user_timezone: User's timezone
            
        Returns:
            Reminder time in UTC
        """
        # Ensure event_start is timezone-aware
        if event_start.tzinfo is None:
            event_start = pytz.UTC.localize(event_start)

        # Calculate reminder time
        reminder_time = event_start - timedelta(hours=advance_hours)

        # Convert to UTC if not already
        if reminder_time.tzinfo != pytz.UTC:
            reminder_time = reminder_time.astimezone(pytz.UTC)

        return reminder_time

    async def should_send_reminder(self, event: CalendarEvent) -> bool:
        """
        Check if reminder should be sent for an event.
        
        Args:
            event: Calendar event
            
        Returns:
            True if reminder should be sent
        """
        # Check if event is deleted
        if event.deleted_at is not None:
            return False

        # Check if reminders are enabled for this event
        if not event.reminder_enabled:
            return False

        # Check if event is in the past
        if event.start_time < datetime.utcnow().replace(tzinfo=pytz.UTC):
            return False

        # Check if reminder already sent
        existing_log = self.db.execute(
            select(ReminderLog).where(
                ReminderLog.event_id == event.id,
                ReminderLog.status.in_([MessageStatus.SENT, MessageStatus.DELIVERED, MessageStatus.READ])
            )
        ).scalar_one_or_none()

        if existing_log:
            return False

        return True

    async def schedule_reminder(
        self,
        event: CalendarEvent,
        user_phone: str,
        user_timezone: str = "UTC"
    ) -> Optional[ReminderLog]:
        """
        Schedule a reminder for an event.
        
        Args:
            event: Calendar event
            user_phone: User's phone number
            user_timezone: User's timezone
            
        Returns:
            Created reminder log or None if not scheduled
        """
        # Check if should send reminder
        if not await self.should_send_reminder(event):
            return None

        # Calculate reminder time
        reminder_time = self.calculate_reminder_time(
            event.start_time,
            advance_hours=settings.default_reminder_hours,
            user_timezone=user_timezone
        )

        # Don't schedule if reminder time is in the past
        if reminder_time < datetime.utcnow().replace(tzinfo=pytz.UTC):
            return None

        # Create reminder log
        reminder_log = ReminderLog(
            event_id=event.id,
            phone_number=user_phone,
            template_name="event_reminder_24h",
            status=MessageStatus.SCHEDULED,
            scheduled_time=reminder_time,
            retry_count=0
        )

        self.db.add(reminder_log)
        self.db.commit()
        self.db.refresh(reminder_log)

        return reminder_log

    def get_pending_reminders(self) -> list[ReminderLog]:
        """
        Get reminders that are due to be sent.
        
        Returns:
            List of pending reminder logs
        """
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)

        reminders = self.db.execute(
            select(ReminderLog).where(
                ReminderLog.status == MessageStatus.SCHEDULED,
                ReminderLog.scheduled_time <= now
            )
        ).scalars().all()

        return list(reminders)

    def mark_reminder_sent(
        self,
        reminder_log: ReminderLog,
        message_id: str
    ) -> None:
        """
        Mark reminder as sent.
        
        Args:
            reminder_log: Reminder log
            message_id: WhatsApp message ID
        """
        reminder_log.status = MessageStatus.SENT
        reminder_log.message_id = message_id
        reminder_log.sent_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
        self.db.commit()

    def mark_reminder_failed(
        self,
        reminder_log: ReminderLog,
        error_message: str
    ) -> None:
        """
        Mark reminder as failed.
        
        Args:
            reminder_log: Reminder log
            error_message: Error message
        """
        reminder_log.status = MessageStatus.FAILED
        reminder_log.error_message = error_message
        reminder_log.retry_count += 1
        self.db.commit()

    def get_failed_reminders(self) -> list[ReminderLog]:
        """
        Get failed reminders that can be retried.
        
        Returns:
            List of failed reminder logs
        """
        reminders = self.db.execute(
            select(ReminderLog).where(
                ReminderLog.status == MessageStatus.FAILED,
                ReminderLog.retry_count < settings.max_retry_attempts
            )
        ).scalars().all()

        return list(reminders)
