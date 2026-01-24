"""Celery tasks for calendar sync and reminder sending."""

import logging
from typing import Dict, Any
from sqlalchemy import select

from src.celery_app import celery_app
from src.database import SessionLocal
from src.models import CalendarEvent, UserPreference
from src.services.calendar_sync_service import CalendarSyncService
from src.services.reminder_engine import ReminderEngine
from src.services.message_service import MessageService
from src.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="src.tasks.celery_tasks.sync_calendars_task")
def sync_calendars_task() -> Dict[str, Any]:
    """
    Periodic task to sync calendars from Google Calendar.
    
    Returns:
        Sync statistics
    """
    logger.info("Starting calendar sync task")
    
    db = SessionLocal()
    try:
        sync_service = CalendarSyncService(db)
        stats = sync_service.sync_calendar()
        
        logger.info(
            f"Calendar sync completed: "
            f"{stats.events_added} added, "
            f"{stats.events_updated} updated, "
            f"{stats.events_deleted} deleted"
        )
        
        return stats.to_dict()
        
    except Exception as e:
        logger.error(f"Calendar sync failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task(name="src.tasks.celery_tasks.schedule_pending_reminders_task")
def schedule_pending_reminders_task() -> Dict[str, Any]:
    """
    Periodic task to schedule reminders for upcoming events.
    
    Returns:
        Statistics about scheduled reminders
    """
    logger.info("Starting reminder scheduling task")
    
    db = SessionLocal()
    try:
        reminder_engine = ReminderEngine(db)
        sync_service = CalendarSyncService(db)
        
        # Get user preferences
        user_pref = db.execute(
            select(UserPreference).where(
                UserPreference.user_email == settings.user_email
            )
        ).scalar_one_or_none()
        
        if not user_pref or not user_pref.enabled:
            logger.info("User reminders are disabled")
            return {"scheduled": 0, "message": "Reminders disabled"}
        
        # Get upcoming events (next 48 hours)
        upcoming_events = sync_service.get_upcoming_events(hours_ahead=48)
        
        scheduled_count = 0
        for event in upcoming_events:
            reminder_log = reminder_engine.schedule_reminder(
                event=event,
                user_phone=user_pref.phone_number,
                user_timezone=user_pref.timezone
            )
            if reminder_log:
                scheduled_count += 1
        
        logger.info(f"Scheduled {scheduled_count} reminders")
        
        return {
            "scheduled": scheduled_count,
            "total_events": len(upcoming_events)
        }
        
    except Exception as e:
        logger.error(f"Reminder scheduling failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task(name="src.tasks.celery_tasks.process_pending_reminders_task")
def process_pending_reminders_task() -> Dict[str, Any]:
    """
    Periodic task to process and send pending reminders.
    
    Returns:
        Statistics about sent reminders
    """
    logger.info("Starting reminder processing task")
    
    db = SessionLocal()
    try:
        reminder_engine = ReminderEngine(db)
        message_service = MessageService(db)
        
        # Get user preferences for timezone
        user_pref = db.execute(
            select(UserPreference).where(
                UserPreference.user_email == settings.user_email
            )
        ).scalar_one_or_none()
        
        user_timezone = user_pref.timezone if user_pref else "UTC"
        
        # Get pending reminders
        pending_reminders = reminder_engine.get_pending_reminders()
        
        sent_count = 0
        failed_count = 0
        
        for reminder_log in pending_reminders:
            # Get associated event
            event = db.execute(
                select(CalendarEvent).where(
                    CalendarEvent.id == reminder_log.event_id
                )
            ).scalar_one_or_none()
            
            if not event:
                logger.warning(f"Event not found for reminder {reminder_log.id}")
                continue
            
            # Send reminder
            success = message_service.send_reminder(
                reminder_log=reminder_log,
                event=event,
                user_timezone=user_timezone
            )
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
        
        logger.info(
            f"Processed {len(pending_reminders)} reminders: "
            f"{sent_count} sent, {failed_count} failed"
        )
        
        return {
            "total": len(pending_reminders),
            "sent": sent_count,
            "failed": failed_count
        }
        
    except Exception as e:
        logger.error(f"Reminder processing failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task(
    name="src.tasks.celery_tasks.send_reminder_task",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def send_reminder_task(self, event_id: str, reminder_log_id: str) -> Dict[str, Any]:
    """
    Task to send a single reminder.
    
    Args:
        event_id: Calendar event ID
        reminder_log_id: Reminder log ID
        
    Returns:
        Result dictionary
    """
    logger.info(f"Sending reminder for event {event_id}")
    
    db = SessionLocal()
    try:
        message_service = MessageService(db)
        reminder_engine = ReminderEngine(db)
        
        # Get event and reminder log
        event = db.execute(
            select(CalendarEvent).where(CalendarEvent.id == event_id)
        ).scalar_one_or_none()
        
        reminder_log = db.execute(
            select(ReminderLog).where(ReminderLog.id == reminder_log_id)
        ).scalar_one_or_none()
        
        if not event or not reminder_log:
            return {"success": False, "message": "Event or reminder log not found"}
        
        # Get user timezone
        user_pref = db.execute(
            select(UserPreference).where(
                UserPreference.user_email == settings.user_email
            )
        ).scalar_one_or_none()
        
        user_timezone = user_pref.timezone if user_pref else "UTC"
        
        # Send reminder
        success = message_service.send_reminder(
            reminder_log=reminder_log,
            event=event,
            user_timezone=user_timezone
        )
        
        if success:
            logger.info(f"Reminder sent successfully for event {event_id}")
            return {"success": True, "message": "Reminder sent"}
        else:
            logger.warning(f"Failed to send reminder for event {event_id}")
            # Retry the task
            raise self.retry(exc=Exception("Failed to send reminder"))
            
    except Exception as e:
        logger.error(f"Error sending reminder: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task(name="src.tasks.celery_tasks.retry_failed_messages_task")
def retry_failed_messages_task() -> Dict[str, Any]:
    """
    Periodic task to retry failed messages.
    
    Returns:
        Statistics about retried messages
    """
    logger.info("Starting failed message retry task")
    
    db = SessionLocal()
    try:
        reminder_engine = ReminderEngine(db)
        message_service = MessageService(db)
        
        # Get user preferences
        user_pref = db.execute(
            select(UserPreference).where(
                UserPreference.user_email == settings.user_email
            )
        ).scalar_one_or_none()
        
        user_timezone = user_pref.timezone if user_pref else "UTC"
        
        # Get failed reminders
        failed_reminders = reminder_engine.get_failed_reminders()
        
        retried_count = 0
        success_count = 0
        
        for reminder_log in failed_reminders:
            # Get associated event
            event = db.execute(
                select(CalendarEvent).where(
                    CalendarEvent.id == reminder_log.event_id
                )
            ).scalar_one_or_none()
            
            if not event:
                continue
            
            # Reset status to scheduled for retry
            from src.models.reminder_log import MessageStatus
            reminder_log.status = MessageStatus.SCHEDULED
            db.commit()
            
            # Try to send
            success = message_service.send_reminder(
                reminder_log=reminder_log,
                event=event,
                user_timezone=user_timezone
            )
            
            retried_count += 1
            if success:
                success_count += 1
        
        logger.info(
            f"Retried {retried_count} failed messages: "
            f"{success_count} succeeded"
        )
        
        return {
            "retried": retried_count,
            "succeeded": success_count,
            "failed": retried_count - success_count
        }
        
    except Exception as e:
        logger.error(f"Failed message retry task failed: {str(e)}")
        raise
    finally:
        db.close()
