"""FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.config import settings
from src.database import get_db, init_db
from src.models import CalendarEvent, ReminderLog, UserPreference
from src.models.reminder_log import MessageStatus
from src.services.calendar_sync_service import CalendarSyncService
from src.services.message_service import MessageService
from src.services.reminder_engine import ReminderEngine

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting WhatsApp Calendar Reminder API")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down WhatsApp Calendar Reminder API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Automated WhatsApp reminder system for Google Calendar events",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health & Status Endpoints

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


@app.get("/status")
async def get_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get system status."""
    # Count events
    total_events = db.execute(
        select(func.count(CalendarEvent.id)).where(
            CalendarEvent.deleted_at.is_(None)
        )
    ).scalar()
    
    # Count reminders by status
    scheduled_reminders = db.execute(
        select(func.count(ReminderLog.id)).where(
            ReminderLog.status == MessageStatus.SCHEDULED
        )
    ).scalar()
    
    sent_reminders = db.execute(
        select(func.count(ReminderLog.id)).where(
            ReminderLog.status == MessageStatus.SENT
        )
    ).scalar()
    
    failed_reminders = db.execute(
        select(func.count(ReminderLog.id)).where(
            ReminderLog.status == MessageStatus.FAILED
        )
    ).scalar()
    
    return {
        "status": "operational",
        "events": {
            "total": total_events
        },
        "reminders": {
            "scheduled": scheduled_reminders,
            "sent": sent_reminders,
            "failed": failed_reminders
        }
    }


# Calendar Management Endpoints

@app.post("/sync")
async def trigger_sync(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Trigger manual calendar sync."""
    try:
        sync_service = CalendarSyncService(db)
        stats = await sync_service.sync_calendar()
        return {
            "success": True,
            "message": "Calendar sync completed",
            "stats": stats.to_dict()
        }
    except Exception as e:
        logger.error(f"Sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events")
async def list_events(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """List upcoming events."""
    events = db.execute(
        select(CalendarEvent).where(
            CalendarEvent.deleted_at.is_(None),
            CalendarEvent.start_time >= datetime.utcnow()
        ).order_by(CalendarEvent.start_time).limit(limit).offset(offset)
    ).scalars().all()
    
    return {
        "events": [event.to_dict() for event in events],
        "total": len(events)
    }


@app.get("/events/{event_id}")
async def get_event(event_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get event details."""
    event = db.execute(
        select(CalendarEvent).where(CalendarEvent.id == event_id)
    ).scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event.to_dict()


# Reminder Management Endpoints

@app.get("/reminders")
async def list_reminders(
    status: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """List reminders."""
    query = select(ReminderLog)
    
    if status:
        try:
            status_enum = MessageStatus(status)
            query = query.where(ReminderLog.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    reminders = db.execute(
        query.order_by(ReminderLog.scheduled_time.desc()).limit(limit).offset(offset)
    ).scalars().all()
    
    return {
        "reminders": [reminder.to_dict() for reminder in reminders],
        "total": len(reminders)
    }


@app.put("/events/{event_id}/reminder")
async def toggle_reminder(
    event_id: str,
    enabled: bool,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Enable or disable reminder for an event."""
    event = db.execute(
        select(CalendarEvent).where(CalendarEvent.id == event_id)
    ).scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.reminder_enabled = enabled
    db.commit()
    
    return {
        "success": True,
        "message": f"Reminder {'enabled' if enabled else 'disabled'}",
        "event": event.to_dict()
    }


@app.post("/reminders/test")
async def send_test_reminder(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Send a test reminder."""
    # Get user preferences
    user_pref = db.execute(
        select(UserPreference).where(
            UserPreference.user_email == settings.user_email
        )
    ).scalar_one_or_none()
    
    if not user_pref:
        raise HTTPException(
            status_code=404,
            detail="User preferences not found. Please set up user preferences first."
        )
    
    message_service = MessageService(db)
    result = await message_service.send_test_reminder(
        phone_number=user_pref.phone_number,
        user_timezone=user_pref.timezone
    )
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])


# Logs & History Endpoints

@app.get("/logs")
async def get_logs(
    event_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Query message logs."""
    query = select(ReminderLog)
    
    if event_id:
        query = query.where(ReminderLog.event_id == event_id)
    
    if status:
        try:
            status_enum = MessageStatus(status)
            query = query.where(ReminderLog.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    logs = db.execute(
        query.order_by(ReminderLog.created_at.desc()).limit(limit).offset(offset)
    ).scalars().all()
    
    return {
        "logs": [log.to_dict() for log in logs],
        "total": len(logs)
    }


@app.get("/logs/{log_id}")
async def get_log(log_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get log details."""
    log = db.execute(
        select(ReminderLog).where(ReminderLog.id == log_id)
    ).scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    return log.to_dict()


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get delivery statistics."""
    # Total reminders by status
    stats_by_status = {}
    for status in MessageStatus:
        count = db.execute(
            select(func.count(ReminderLog.id)).where(
                ReminderLog.status == status
            )
        ).scalar()
        stats_by_status[status.value] = count
    
    # Success rate
    total = sum(stats_by_status.values())
    success = stats_by_status.get("sent", 0) + stats_by_status.get("delivered", 0)
    success_rate = (success / total * 100) if total > 0 else 0
    
    return {
        "total_reminders": total,
        "by_status": stats_by_status,
        "success_rate": round(success_rate, 2)
    }


# User Preferences Endpoints

@app.get("/preferences")
async def get_preferences(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get user preferences."""
    user_pref = db.execute(
        select(UserPreference).where(
            UserPreference.user_email == settings.user_email
        )
    ).scalar_one_or_none()
    
    if not user_pref:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    return user_pref.to_dict()


@app.put("/preferences")
async def update_preferences(
    phone_number: Optional[str] = None,
    timezone: Optional[str] = None,
    default_reminder_hours: Optional[int] = None,
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update user preferences."""
    user_pref = db.execute(
        select(UserPreference).where(
            UserPreference.user_email == settings.user_email
        )
    ).scalar_one_or_none()
    
    if not user_pref:
        # Create new preferences
        user_pref = UserPreference(
            user_email=settings.user_email,
            phone_number=phone_number or settings.user_phone_number,
            timezone=timezone or settings.user_timezone,
            default_reminder_hours=default_reminder_hours or settings.default_reminder_hours,
            enabled=enabled if enabled is not None else True
        )
        db.add(user_pref)
    else:
        # Update existing preferences
        if phone_number:
            user_pref.phone_number = phone_number
        if timezone:
            user_pref.timezone = timezone
        if default_reminder_hours:
            user_pref.default_reminder_hours = default_reminder_hours
        if enabled is not None:
            user_pref.enabled = enabled
    
    db.commit()
    db.refresh(user_pref)
    
    return {
        "success": True,
        "message": "Preferences updated",
        "preferences": user_pref.to_dict()
    }


# Webhook Endpoints

@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(data: Dict[str, Any]) -> Dict[str, str]:
    """
    WhatsApp delivery status webhook.
    
    This endpoint receives delivery status updates from WhatsApp.
    """
    logger.info(f"Received WhatsApp webhook: {data}")
    
    # TODO: Implement webhook processing
    # Extract message ID and status from webhook payload
    # Update ReminderLog status accordingly
    
    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
