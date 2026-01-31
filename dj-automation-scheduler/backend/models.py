from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime

def generate_uuid():
    return str(uuid.uuid4())

class AudioAsset(Base):
    __tablename__ = "audio_assets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'mix' or 'track'
    audio_url = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    dropbox_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    schedule_events = relationship("ScheduleEvent", back_populates="audio_asset", cascade="all, delete-orphan")

class ScheduleEvent(Base):
    __tablename__ = "schedule_events"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    audio_asset_id = Column(String, ForeignKey("audio_assets.id"), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    audio_asset = relationship("AudioAsset", back_populates="schedule_events")
