from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import AudioAsset, ScheduleEvent
from schemas import (
    AudioAssetCreate, AudioAssetResponse,
    ScheduleEventCreate, ScheduleEventResponse,
    DropboxUploadResponse
)
from dropbox_service import dropbox_service
from datetime import datetime
from typing import Optional
import mimetypes

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Audio Assets CRUD
@router.post("/assets", response_model=AudioAssetResponse)
def create_asset(asset: AudioAssetCreate, db: Session = Depends(get_db)):
    """
    Create a new audio asset
    """
    db_asset = AudioAsset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return AudioAssetResponse.model_validate(db_asset)

@router.get("/assets", response_model=list[AudioAssetResponse])
def list_assets(db: Session = Depends(get_db)):
    """
    List all audio assets
    """
    assets = db.query(AudioAsset).order_by(AudioAsset.created_at.desc()).all()
    return [AudioAssetResponse.model_validate(asset) for asset in assets]

@router.get("/assets/{asset_id}", response_model=AudioAssetResponse)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    """
    Get a specific audio asset
    """
    asset = db.query(AudioAsset).filter(AudioAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AudioAssetResponse.model_validate(asset)

@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: str, db: Session = Depends(get_db)):
    """
    Delete an audio asset
    """
    asset = db.query(AudioAsset).filter(AudioAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Try to delete from Dropbox, but don't fail if it doesn't work
    if asset.dropbox_path:
        try:
            dropbox_service.delete_file(asset.dropbox_path)
            print(f"Deleted from Dropbox: {asset.dropbox_path}")
        except Exception as e:
            print(f"Could not delete from Dropbox (permission issue): {e}")
            # Continue anyway - just delete from database
    
    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted successfully"}

# Schedule Events CRUD
@router.post("/schedule", response_model=ScheduleEventResponse)
def create_schedule_event(event: ScheduleEventCreate, db: Session = Depends(get_db)):
    """
    Create a new schedule event
    Note: Frontend sends times in local timezone, we store them as-is (naive datetime)
    """
    print(f"Creating schedule event:")
    print(f"  Asset ID: {event.audio_asset_id}")
    print(f"  Start: {event.start_at}")
    print(f"  End: {event.end_at}")
    
    # Validate asset exists
    asset = db.query(AudioAsset).filter(AudioAsset.id == event.audio_asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Audio asset not found")
    
    # Validate times
    if event.start_at >= event.end_at:
        raise HTTPException(status_code=400, detail="Start time must be before end time")
    
    # Check for overlapping events
    overlapping = db.query(ScheduleEvent).filter(
        ScheduleEvent.start_at < event.end_at,
        ScheduleEvent.end_at > event.start_at
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=400, detail="Schedule overlaps with existing event")
    
    db_event = ScheduleEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    print(f"  Created event ID: {db_event.id}")
    
    return ScheduleEventResponse.model_validate(db_event)

@router.get("/schedule", response_model=list[ScheduleEventResponse])
def list_schedule_events(db: Session = Depends(get_db)):
    """
    List all schedule events
    """
    events = db.query(ScheduleEvent).order_by(ScheduleEvent.start_at).all()
    return [ScheduleEventResponse.model_validate(event) for event in events]

@router.delete("/schedule/{event_id}")
def delete_schedule_event(event_id: str, db: Session = Depends(get_db)):
    """
    Delete a schedule event
    """
    event = db.query(ScheduleEvent).filter(ScheduleEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Schedule event not found")
    
    db.delete(event)
    db.commit()
    return {"message": "Schedule event deleted successfully"}

# Dropbox Upload
@router.post("/upload", response_model=DropboxUploadResponse)
async def upload_to_dropbox(
    file: UploadFile = File(...),
    folder: str = Form("/dj-assets")
):
    """
    Upload a file to Dropbox and return the shared URL
    """
    try:
        print(f"Attempting to upload file: {file.filename}")
        
        # Read file content
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        
        # Upload to Dropbox
        success, dropbox_path, error = dropbox_service.upload_file(
            file.filename,
            content,
            folder
        )
        
        if not success:
            print(f"Dropbox upload failed: {error}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {error}")
        
        print(f"File uploaded to: {dropbox_path}")
        
        # Create shared link
        shared_url = dropbox_service.create_shared_link(dropbox_path)
        
        if not shared_url:
            print("Failed to create shared link")
            raise HTTPException(status_code=500, detail="Failed to create shared link")
        
        print(f"Shared URL created: {shared_url}")
        
        return DropboxUploadResponse(
            success=True,
            file_path=dropbox_path,
            shared_url=shared_url,
            file_size=len(content),
            message="File uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/dropbox/files")
def list_dropbox_files(folder: str = "/dj-assets"):
    """
    List files in Dropbox folder with metadata
    """
    files = dropbox_service.list_files(folder)
    # Filter to only audio files
    audio_files = [f for f in files if f.get('is_audio', False)]
    return {"files": audio_files, "total": len(audio_files)}

@router.post("/assets/{asset_id}/fix-url")
def fix_asset_url(asset_id: str, db: Session = Depends(get_db)):
    """
    Fix the Dropbox URL for an asset (remove dl=0, add dl=1)
    """
    asset = db.query(AudioAsset).filter(AudioAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    old_url = asset.audio_url
    
    # Fix the URL
    new_url = old_url
    if '?dl=0' in new_url:
        new_url = new_url.replace('?dl=0', '?dl=1')
    if '&dl=0' in new_url:
        new_url = new_url.replace('&dl=0', '&dl=1')
    if not ('dl=1' in new_url or 'dl.dropboxusercontent.com' in new_url):
        new_url = new_url + ('&' if '?' in new_url else '?') + 'dl=1'
    
    asset.audio_url = new_url
    db.commit()
    
    return {
        "message": "URL fixed",
        "old_url": old_url,
        "new_url": new_url
    }

@router.post("/dropbox/import", response_model=AudioAssetResponse)
def import_from_dropbox(
    import_data: dict,
    db: Session = Depends(get_db)
):
    """
    Import a file from Dropbox into the database
    """
    try:
        file_path = import_data.get('file_path')
        title = import_data.get('title')
        type_val = import_data.get('type', 'mix')
        duration_seconds = import_data.get('duration_seconds')
        
        if not all([file_path, title, duration_seconds]):
            raise HTTPException(status_code=400, detail="Missing required fields: file_path, title, duration_seconds")
        
        print(f"Importing file: {file_path}")
        print(f"Title: {title}, Type: {type_val}, Duration: {duration_seconds}")
        
        # Get file info from Dropbox
        files = dropbox_service.list_files()
        file_info = next((f for f in files if f['path'] == file_path), None)
        
        if not file_info:
            print(f"File not found in Dropbox: {file_path}")
            raise HTTPException(status_code=404, detail="File not found in Dropbox")
        
        print(f"Found file in Dropbox: {file_info}")
        
        # Check if already imported
        existing = db.query(AudioAsset).filter(AudioAsset.dropbox_path == file_path).first()
        if existing:
            print(f"File already imported: {file_path}")
            raise HTTPException(status_code=400, detail="File already imported")
        
        # Create asset in database
        db_asset = AudioAsset(
            title=title,
            type=type_val,
            audio_url=file_info['shared_url'],
            duration_seconds=int(duration_seconds),
            file_size=file_info['size'],
            dropbox_path=file_path
        )
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        
        print(f"Successfully imported: {title}")
        
        return AudioAssetResponse.model_validate(db_asset)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Import error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
