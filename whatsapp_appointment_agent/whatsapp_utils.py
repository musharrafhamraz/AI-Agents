"""
WhatsApp Cloud API utilities
"""
import requests
from config import settings
from typing import Optional


class WhatsAppAPI:
    """WhatsApp Cloud API wrapper"""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self):
        self.token = settings.whatsapp_api_token
        self.phone_number_id = settings.whatsapp_phone_number_id
    
    def send_message(self, to: str, message: str) -> dict:
        """
        Send a text message to a WhatsApp user
        
        Args:
            to: Phone number in international format (e.g., "1234567890")
            message: Text message to send
        
        Returns:
            API response
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def send_template_message(
        self, 
        to: str, 
        template_name: str, 
        language_code: str = "en",
        components: Optional[list] = None
    ) -> dict:
        """
        Send a template message (for reminders and bulk messages)
        
        Args:
            to: Phone number
            template_name: Name of the approved template
            language_code: Language code
            components: Template components (parameters)
        
        Returns:
            API response
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()


# Singleton instance
whatsapp_api = WhatsAppAPI()
