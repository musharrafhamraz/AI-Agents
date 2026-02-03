from sqlalchemy import Column, Integer, String, JSON, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=False)
    gmail_credentials = Column(JSON)  # Stores OAuth tokens
    check_frequency = Column(String, default="hourly")
    importance_threshold = Column(Integer, default=7)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    processed_emails = relationship("ProcessedEmail", back_populates="user")
    whatsapp_messages = relationship("WhatsAppMessage", back_populates="user")
