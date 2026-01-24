"""WhatsApp Business API client."""

from typing import Dict, Any, Optional
from enum import Enum
import httpx
from src.config import settings


class WhatsAppMessageStatus(str, Enum):
    """WhatsApp message status."""
    
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class WhatsAppClient:
    """Client for interacting with WhatsApp Business API."""

    def __init__(self) -> None:
        """Initialize WhatsApp client."""
        self.api_url = settings.whatsapp_api_url
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def send_template_message(
        self,
        phone_number: str,
        template_name: str,
        parameters: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Send a template message via WhatsApp Business API.
        
        Args:
            phone_number: Recipient phone number (with country code, e.g., +1234567890)
            template_name: Name of the approved template
            parameters: Dictionary of template parameters
            
        Returns:
            Response from WhatsApp API containing message ID
            
        Raises:
            Exception: If message sending fails
        """
        # Remove any non-numeric characters except +
        phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Build template components
        components = []
        
        # Body component with parameters
        if parameters:
            body_parameters = [
                {"type": "text", "text": value}
                for value in parameters.values()
            ]
            components.append({
                "type": "body",
                "parameters": body_parameters
            })

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": "en_US"  # Changed from "en" to "en_US" for compatibility
                },
                "components": components
            }
        }

        url = f"{self.api_url}/{self.phone_number_id}/messages"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "status": "sent"
                }

            except httpx.HTTPStatusError as error:
                error_data = error.response.json() if error.response else {}
                raise Exception(
                    f"WhatsApp API error: {error.response.status_code} - "
                    f"{error_data.get('error', {}).get('message', 'Unknown error')}"
                )
            except Exception as error:
                raise Exception(f"Failed to send WhatsApp message: {str(error)}")

    async def get_message_status(self, message_id: str) -> WhatsAppMessageStatus:
        """
        Get the status of a sent message.
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            Message status
        """
        # Note: WhatsApp primarily uses webhooks for status updates
        # This is a placeholder for potential future API support
        # In practice, status updates come via webhook callbacks
        return WhatsAppMessageStatus.SENT

    async def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate if a phone number is registered on WhatsApp.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - check format
        phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Must start with + and have at least 10 digits
        if not phone_number.startswith('+'):
            return False
        
        digits = ''.join(c for c in phone_number if c.isdigit())
        return len(digits) >= 10

    def format_event_reminder_message(
        self,
        event_title: str,
        event_time: str,
        event_location: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Format event data into template parameters.
        
        Args:
            event_title: Event title
            event_time: Formatted event time
            event_location: Event location (optional)
            
        Returns:
            Dictionary of template parameters
        """
        parameters = {
            "event_title": event_title,
            "event_time": event_time,
        }
        
        if event_location:
            parameters["event_location"] = event_location
        
        return parameters
