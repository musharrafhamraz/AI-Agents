from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class ProcessedEmail(Base, TimestampMixin):
    __tablename__ = "processed_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email_id = Column(String, nullable=False, index=True)  # Gmail message ID
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body_preview = Column(Text)  # First 500 chars
    importance_score = Column(Float, nullable=False)
    summary = Column(Text)
    processed_at = Column(DateTime)
    sent_to_whatsapp = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="processed_emails")
