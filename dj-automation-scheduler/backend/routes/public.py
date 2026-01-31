from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import ScheduleEvent, AudioAsset
from schemas import NowPlayingResponse, AudioAssetResponse, ScheduleEventResponse
from datetime import datetime, timezone
from sqlalchemy import and_

router = APIRouter(prefix="/api", tags=["public"])

@router.get("/now-playing", response_model=NowPlayingResponse)
def get_now_playing(db: Session = Depends(get_db)):
    """
    Get the currently playing track/mix based on schedule
    Calculates seek position based on elapsed time
    Note: Uses local server time (naive datetime) to match schedule times
    """
    # Use local time (naive datetime) to match what's stored in database
    # Remove microseconds for cleaner comparison
    current_time = datetime.now().replace(microsecond=0)
    
    print(f"\n=== NOW PLAYING CHECK ===")
    print(f"Current local time: {current_time}")
    
    # Get all events for debugging
    all_events = db.query(ScheduleEvent).all()
    print(f"Total events in database: {len(all_events)}")
    
    for evt in all_events:
        # Ensure event times are naive datetime (no timezone)
        start_time = evt.start_at.replace(tzinfo=None) if evt.start_at.tzinfo else evt.start_at
        end_time = evt.end_at.replace(tzinfo=None) if evt.end_at.tzinfo else evt.end_at
        
        print(f"\nEvent: {evt.audio_asset.title}")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")
        print(f"  Current: {current_time}")
        print(f"  Start <= Current: {start_time <= current_time}")
        print(f"  End >= Current: {end_time >= current_time}")
        print(f"  Is Active: {start_time <= current_time <= end_time}")
    
    # Find active schedule event - use raw SQL to be explicit
    active_events = []
    for event in all_events:
        start_time = event.start_at.replace(tzinfo=None) if event.start_at.tzinfo else event.start_at
        end_time = event.end_at.replace(tzinfo=None) if event.end_at.tzinfo else event.end_at
        
        if start_time <= current_time <= end_time:
            active_events.append(event)
    
    if active_events:
        active_event = active_events[0]
        print(f"\n✓ Active event found: {active_event.audio_asset.title}")
        
        start_time = active_event.start_at.replace(tzinfo=None) if active_event.start_at.tzinfo else active_event.start_at
        
        # Calculate seek position
        elapsed = (current_time - start_time).total_seconds()
        seek_position = max(0, int(elapsed))  # Ensure non-negative
        
        print(f"  Elapsed time: {elapsed} seconds, Seek position: {seek_position}")
        
        # Get next event
        next_events = [e for e in all_events if (e.start_at.replace(tzinfo=None) if e.start_at.tzinfo else e.start_at) > current_time]
        next_event = sorted(next_events, key=lambda e: e.start_at)[0] if next_events else None
        
        return NowPlayingResponse(
            is_playing=True,
            current_asset=AudioAssetResponse.model_validate(active_event.audio_asset),
            seek_position=seek_position,
            next_event=ScheduleEventResponse.model_validate(next_event) if next_event else None,
            message="Currently playing"
        )
    
    # No active event, check for upcoming
    future_events = [e for e in all_events if (e.start_at.replace(tzinfo=None) if e.start_at.tzinfo else e.start_at) > current_time]
    
    if future_events:
        next_event = sorted(future_events, key=lambda e: e.start_at)[0]
        next_start = next_event.start_at.replace(tzinfo=None) if next_event.start_at.tzinfo else next_event.start_at
        
        print(f"\n→ Next event: {next_event.audio_asset.title}")
        print(f"  Next event start: {next_start}")
        
        time_until = (next_start - current_time).total_seconds()
        minutes = int(time_until // 60)
        
        print(f"  Time until next event: {time_until} seconds ({minutes} minutes)")
        
        return NowPlayingResponse(
            is_playing=False,
            next_event=ScheduleEventResponse.model_validate(next_event),
            message=f"Next track starts in {minutes} minutes"
        )
    
    print("\n✗ No scheduled content")
    return NowPlayingResponse(
        is_playing=False,
        message="No scheduled content"
    )

@router.get("/schedule", response_model=list[ScheduleEventResponse])
def get_schedule(db: Session = Depends(get_db)):
    """
    Get all scheduled events
    """
    events = db.query(ScheduleEvent).order_by(ScheduleEvent.start_at).all()
    return [ScheduleEventResponse.model_validate(event) for event in events]

@router.get("/debug/time")
def debug_time(db: Session = Depends(get_db)):
    """
    Debug endpoint to check time handling
    """
    current_local = datetime.now()
    
    # Get all schedule events
    events = db.query(ScheduleEvent).all()
    
    event_info = []
    for event in events:
        time_diff = (event.start_at - current_local).total_seconds()
        event_info.append({
            "title": event.audio_asset.title,
            "start_at": str(event.start_at),
            "end_at": str(event.end_at),
            "time_until_start_seconds": time_diff,
            "time_until_start_minutes": time_diff / 60,
            "is_active": event.start_at <= current_local <= event.end_at
        })
    
    return {
        "current_local_time": str(current_local),
        "events": event_info,
        "note": "All times are in local server timezone (naive datetime)"
    }
