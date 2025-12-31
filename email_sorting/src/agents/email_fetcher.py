"""Email Fetcher Agent - Retrieves emails from providers"""

from typing import Dict, Any, List
from datetime import datetime

from ..config import settings
from ..tools.gmail_tools import get_gmail_client


class EmailFetcherAgent:
    """Agent that fetches emails from email providers"""
    
    def __init__(self):
        self.provider = settings.EMAIL_PROVIDER
    
    def fetch_emails(self, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Fetch unprocessed emails from the configured provider.
        
        Args:
            max_results: Maximum number of emails to fetch
        
        Returns:
            List of email states ready for processing
        """
        max_results = max_results or settings.BATCH_SIZE
        
        if self.provider == "gmail":
            return self._fetch_from_gmail(max_results)
        elif self.provider == "outlook":
            return self._fetch_from_outlook(max_results)
        elif self.provider == "imap":
            return self._fetch_from_imap(max_results)
        else:
            raise ValueError(f"Unsupported email provider: {self.provider}")
    
    def _fetch_from_gmail(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail"""
        client = get_gmail_client()
        
        # Authenticate if needed
        if not client.service:
            client.authenticate()
        
        # Fetch emails
        raw_emails = client.fetch_unread_emails(max_results)
        
        # Convert to EmailState format
        email_states = []
        for email in raw_emails:
            state = self._convert_to_state(email)
            email_states.append(state)
        
        return email_states
    
    def _fetch_from_outlook(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch emails from Outlook (to be implemented)"""
        # TODO: Implement Outlook integration
        raise NotImplementedError("Outlook integration not yet implemented")
    
    def _fetch_from_imap(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch emails from IMAP (to be implemented)"""
        # TODO: Implement IMAP integration
        raise NotImplementedError("IMAP integration not yet implemented")
    
    def _convert_to_state(self, raw_email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw email data to EmailState format.
        
        Args:
            raw_email: Raw email data from provider
        
        Returns:
            EmailState dictionary
        """
        return {
            "message_id": raw_email.get("message_id", ""),
            "sender": raw_email.get("sender", ""),
            "recipient": raw_email.get("recipient", ""),
            "subject": raw_email.get("subject", ""),
            "body": raw_email.get("body", ""),
            "body_html": None,
            "received_at": raw_email.get("date", datetime.now().isoformat()),
            "thread_id": raw_email.get("thread_id"),
            "has_attachments": raw_email.get("has_attachments", False),
            "attachment_count": 0,
            
            # Initialize processing fields
            "processing_stage": "fetched",
            "requires_human_review": False,
            "action_items": [],
            "actions": [],
            "labels": [],
            "retry_count": 0,
            
            # Context (to be populated by memory systems)
            "sender_history": None,
            "similar_emails": None,
            
            # Results (to be populated by agents)
            "classification": None,
            "classification_confidence": None,
            "classification_reasoning": None,
            "priority_score": None,
            "urgency_level": None,
            "recommended_response_time": None,
            "priority_reasoning": None,
            "intent": None,
            "intent_confidence": None,
            "requires_response": None,
            "intent_reasoning": None,
            "overall_confidence": None,
            
            # Error handling
            "error": None,
            "processed_at": None,
            "processing_time_ms": None
        }


# Standalone function for easy import
def fetch_emails(max_results: int = None) -> List[Dict[str, Any]]:
    """
    Fetch emails from configured provider.
    
    Args:
        max_results: Maximum number of emails to fetch
    
    Returns:
        List of email states
    """
    fetcher = EmailFetcherAgent()
    return fetcher.fetch_emails(max_results)
