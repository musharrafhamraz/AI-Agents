"""Message service for sending WhatsApp reminders."""

from datetime import datetime
from typing import Dict, Any, Optional
import pytz
from sqlalchemy.orm import Session

from src.integrations.whatsapp_client import WhatsAppClient
from src.models import CalendarEvent, ReminderLog
from src.services.reminder_engine import ReminderEngine


class MessageService:
    """Service for sending WhatsApp reminder messages."""

    def __init__(self, db: Session):
        """
        Initialize message service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.whatsapp_client = WhatsAppClient()
        self.reminder_engine = ReminderEngine(db)

    def format_event_time(
        self,
        event_start: datetime,
        user_timezone: str = "UTC"
    ) -> str:
        """
        Format event time for display.
        
        Args:
            event_start: Event start time
            user_timezone: User's timezone
            
        Returns:
            Formatted time string
        """
        # Convert to user's timezone
        tz = pytz.timezone(user_timezone)
        local_time = event_start.astimezone(tz)
        
        # Format: "Monday, January 23, 2026 at 2:00 PM"
        return local_time.strftime("%A, %B %d, %Y at %I:%M %p")

    async def send_reminder(
        self,
        reminder_log: ReminderLog,
        event: CalendarEvent,
        user_timezone: str = "UTC"
    ) -> bool:
        """
        Send a reminder message.
        
        Args:
            reminder_log: Reminder log entry
            event: Calendar event
            user_timezone: User's timezone
            
        Returns:
            True if sent successfully
        """
        try:
            # Format event time
            event_time = self.format_event_time(event.start_time, user_timezone)

            # Prepare template parameters
            parameters = {
                "event_title": event.title,
                "event_time": event_time,
            }

            if event.location:
                parameters["event_location"] = event.location

            # Send message
            result = await self.whatsapp_client.send_template_message(
                phone_number=reminder_log.phone_number,
                template_name=reminder_log.template_name,
                parameters=parameters
            )

            # Update reminder log
            if result.get("success"):
                self.reminder_engine.mark_reminder_sent(
                    reminder_log,
                    result.get("message_id", "")
                )
                return True
            else:
                self.reminder_engine.mark_reminder_failed(
                    reminder_log,
                    "Failed to send message"
                )
                return False

        except Exception as e:
            # Mark as failed
            self.reminder_engine.mark_reminder_failed(
                reminder_log,
                str(e)
            )
            return False

    async def send_test_reminder(
        self,
        phone_number: str,
        user_timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Send a test reminder message.
        
        Args:
            phone_number: Phone number to send to
            user_timezone: User's timezone
            
        Returns:
            Result dictionary
        """
        try:
            # Try to send with custom template first
            try:
                # Create test event data
                test_time = datetime.now(pytz.UTC) + timedelta(hours=24)
                event_time = self.format_event_time(test_time, user_timezone)

                parameters = {
                    "event_title": "Test Event",
                    "event_time": event_time,
                    "event_location": "Test Location"
                }

                # Send message with custom template
                result = await self.whatsapp_client.send_template_message(
                    phone_number=phone_number,
                    template_name="event_reminder_24h",
                    parameters=parameters
                )

                return {
                    "success": True,
                    "message": "Test reminder sent successfully with custom template",
                    "message_id": result.get("message_id")
                }
                
            except Exception as template_error:
                # If custom template fails, fall back to hello_world (works with any phone number)
                if "template" in str(template_error).lower() or "131047" in str(template_error) or "131030" in str(template_error):
                    result = await self.whatsapp_client.send_template_message(
                        phone_number=phone_number,
                        template_name="hello_world",
                        parameters={}
                    )

                    return {
                        "success": True,
                        "message": "Test message sent successfully using 'hello_world' template. Create 'event_reminder_24h' template for proper calendar reminders.",
                        "message_id": result.get("message_id"),
                        "note": "Using fallback template. Please create 'event_reminder_24h' template in Meta Business Manager for proper calendar reminders."
                    }
                else:
                    # Re-raise if it's not a template error
                    raise template_error

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send test reminder: {str(e)}"
            }


from datetime import timedelta
