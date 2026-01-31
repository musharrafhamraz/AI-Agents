from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

# Audio Asset Schemas
class AudioAssetBase(BaseModel):
    title: str
    type: Literal["mix", "track"]
    audio_url: str
    duration_seconds: int
    file_size: Optional[int] = None
    dropbox_path: Optional[str] = None

class AudioAssetCreate(AudioAssetBase):
    pass

class AudioAssetResponse(AudioAssetBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schedule Event Schemas
class ScheduleEventBase(BaseModel):
    audio_asset_id: str
    start_at: datetime
    end_at: datetime

class ScheduleEventCreate(ScheduleEventBase):
    pass

class ScheduleEventResponse(ScheduleEventBase):
    id: str
    created_at: datetime
    audio_asset: Optional[AudioAssetResponse] = None
    
    class Config:
        from_attributes = True

# Now Playing Response
class NowPlayingResponse(BaseModel):
    is_playing: bool
    current_asset: Optional[AudioAssetResponse] = None
    seek_position: Optional[int] = None  # in seconds
    next_event: Optional[ScheduleEventResponse] = None
    message: Optional[str] = None

# Dropbox Upload Response
class DropboxUploadResponse(BaseModel):
    success: bool
    file_path: str
    shared_url: Optional[str] = None
    file_size: int
    message: str
