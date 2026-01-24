"""Calendar synchronization service."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.integrations.google_calendar import GoogleCalendarClient, CalendarEventData
from src.models import CalendarEvent, SyncState
from src.models.sync_state import SyncStatus
from src.config import settings


class SyncStats:
    """Statistics from a sync operation."""

    def __init__(self):
        self.events_added = 0
        self.events_updated = 0
        self.events_deleted = 0
        self.errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "events_added": self.events_added,
            "events_updated": self.events_updated,
            "events_deleted": self.events_deleted,
            "errors": self.errors,
        }


class CalendarSyncService:
    """Service for synchronizing Google Calendar events with database."""

    def __init__(self, db: Session):
        """
        Initialize calendar sync service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.calendar_client = GoogleCalendarClient()

    async def sync_calendar(
        self,
        calendar_id: Optional[str] = None
    ) -> SyncStats:
        """
        Synchronize calendar events from Google Calendar.
        
        Args:
            calendar_id: Calendar ID to sync (defaults to primary)
            
        Returns:
            Sync statistics
        """
        calendar_id = calendar_id or settings.google_calendar_id
        stats = SyncStats()

        try:
            # Get existing sync state
            sync_state = self.db.execute(
                select(SyncState).where(SyncState.calendar_id == calendar_id)
            ).scalar_one_or_none()

            # Get sync token if exists
            sync_token = sync_state.sync_token if sync_state else None

            # Sync events from Google Calendar
            events, new_sync_token = self.calendar_client.sync_events(
                sync_token=sync_token,
                calendar_id=calendar_id
            )

            # Process each event
            for event_data in events:
                await self._process_event(event_data, calendar_id, stats)

            # Update sync state
            if sync_state:
                sync_state.sync_token = new_sync_token
                sync_state.last_sync_time = datetime.utcnow()
                sync_state.last_sync_status = SyncStatus.SUCCESS
                sync_state.error_message = None
            else:
                sync_state = SyncState(
                    calendar_id=calendar_id,
                    sync_token=new_sync_token,
                    last_sync_time=datetime.utcnow(),
                    last_sync_status=SyncStatus.SUCCESS
                )
                self.db.add(sync_state)

            self.db.commit()

        except Exception as e:
            stats.errors.append(str(e))
            
            # Update sync state with error
            if sync_state:
                sync_state.last_sync_status = SyncStatus.FAILED
                sync_state.error_message = str(e)
                self.db.commit()

        return stats

    async def _process_event(
        self,
        event_data: CalendarEventData,
        calendar_id: str,
        stats: SyncStats
    ) -> None:
        """
        Process a single calendar event.
        
        Args:
            event_data: Event data from Google Calendar
            calendar_id: Calendar ID
            stats: Sync statistics to update
        """
        # Check if event exists
        existing_event = self.db.execute(
            select(CalendarEvent).where(
                CalendarEvent.google_event_id == event_data.event_id
            )
        ).scalar_one_or_none()

        if existing_event:
            # Update existing event
            existing_event.title = event_data.title
            existing_event.description = event_data.description
            existing_event.start_time = event_data.start_time
            existing_event.end_time = event_data.end_time
            existing_event.location = event_data.location
            existing_event.attendees = {"attendees": event_data.attendees}
            existing_event.updated_at = datetime.utcnow()
            stats.events_updated += 1
        else:
            # Create new event
            new_event = CalendarEvent(
                google_event_id=event_data.event_id,
                calendar_id=calendar_id,
                title=event_data.title,
                description=event_data.description,
                start_time=event_data.start_time,
                end_time=event_data.end_time,
                location=event_data.location,
                attendees={"attendees": event_data.attendees},
                reminder_enabled=True
            )
            self.db.add(new_event)
            stats.events_added += 1

    async def handle_event_cancellation(self, event_id: str) -> None:
        """
        Handle event cancellation (soft delete).
        
        Args:
            event_id: Google Calendar event ID
        """
        event = self.db.execute(
            select(CalendarEvent).where(
                CalendarEvent.google_event_id == event_id
            )
        ).scalar_one_or_none()

        if event:
            event.deleted_at = datetime.utcnow()
            self.db.commit()

    def get_upcoming_events(self, hours_ahead: int = 48) -> List[CalendarEvent]:
        """
        Get upcoming events from database.
        
        Args:
            hours_ahead: Number of hours to look ahead
            
        Returns:
            List of upcoming events
        """
        from datetime import timedelta
        
        now = datetime.utcnow()
        time_max = now + timedelta(hours=hours_ahead)

        events = self.db.execute(
            select(CalendarEvent).where(
                CalendarEvent.start_time >= now,
                CalendarEvent.start_time <= time_max,
                CalendarEvent.deleted_at.is_(None),
                CalendarEvent.reminder_enabled == True
            ).order_by(CalendarEvent.start_time)
        ).scalars().all()

        return list(events)
