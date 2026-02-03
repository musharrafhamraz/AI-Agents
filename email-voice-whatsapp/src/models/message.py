from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class WhatsAppMessage(Base, TimestampMixin):
    __tablename__ = "whatsapp_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email_ids = Column(JSON)  # List of email IDs included in this message
    message_text = Column(Text, nullable=False)
    twilio_message_sid = Column(String)
    status = Column(String, default="pending")  # pending, sent, delivered, failed
    error_message = Column(Text)
    sent_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="whatsapp_messages")
