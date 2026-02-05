from twilio.rest import Client
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for sending messages via Twilio WhatsApp"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
    
    def send_message(self, to_number: str, message: str) -> dict:
        """Send a WhatsApp message"""
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            logger.info(f"Sending WhatsApp message to {to_number}")
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"Message sent successfully. SID: {message_obj.sid}")
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'sent_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'sent_at': datetime.utcnow()
            }
    
    def format_email_summary_message(self, summaries: list[dict]) -> str:
        """Format multiple email summaries into a single WhatsApp message"""
        if not summaries:
            return "No important emails at this time."
        
        count = len(summaries)
        message_parts = [f"📧 *Email Summary* ({count} important email{'s' if count > 1 else ''})\n"]
        
        for i, summary_data in enumerate(summaries, 1):
            sender = summary_data['sender']
            subject = summary_data['subject']
            summary = summary_data['summary']
            importance = summary_data['importance']
            
            message_parts.append(
                f"\n*{i}. {sender}*\n"
                f"Subject: {subject}\n"
                f"Priority: {'🔴' if importance >= 8 else '🟡' if importance >= 6 else '🟢'} {importance}/10\n"
                f"{summary}\n"
                f"{'─' * 30}"
            )
        
        return '\n'.join(message_parts)
    
    def send_email_summaries(self, to_number: str, summaries: list[dict]) -> dict:
        """Send formatted email summaries via WhatsApp"""
        message = self.format_email_summary_message(summaries)
        return self.send_message(to_number, message)
    
    def get_message_status(self, message_sid: str) -> Optional[str]:
        """Get the status of a sent message"""
        try:
            message = self.client.messages(message_sid).fetch()
            return message.status
        except Exception as e:
            logger.error(f"Error fetching message status: {str(e)}")
            return None
