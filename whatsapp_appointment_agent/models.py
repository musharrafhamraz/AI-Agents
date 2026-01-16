"""
Database models for WhatsApp Appointment Agent
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Lead(SQLModel, table=True):
    """Lead/Client information"""
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = Field(index=True, unique=True)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    appointments: list["Appointment"] = Relationship(back_populates="lead")


class Appointment(SQLModel, table=True):
    """Appointment information"""
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id")
    
    # Appointment details
    service: str
    appointment_time: datetime
    status: str = Field(default="confirmed")  # confirmed, cancelled, completed
    reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Reminder tracking
    reminder_2h_sent: bool = Field(default=False)
    reminder_1h_sent: bool = Field(default=False)
    
    # Relationship
    lead: Lead = Relationship(back_populates="appointments")
