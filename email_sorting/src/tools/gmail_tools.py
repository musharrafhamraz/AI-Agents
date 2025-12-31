"""Gmail API tools for LangGraph agents"""

import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from langchain.tools import tool

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]


class GmailClient:
    """Gmail API client for email operations"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def authenticate(self, credentials_path: str = "credentials.json", token_path: str = "token.pickle"):
        """
        Authenticate with Gmail API using OAuth2.
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON
            token_path: Path to save/load token
        """
        creds = None
        
        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {credentials_path}\n"
                        "Please download OAuth2 credentials from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def fetch_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from inbox.
        
        Args:
            max_results: Maximum number of emails to fetch
        
        Returns:
            List of email dictionaries
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            # Get list of unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Fetch full message details
            emails = []
            for msg in messages:
                email_data = self._get_message_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def _get_message_details(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """Get full message details"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            header_dict = {h['name']: h['value'] for h in headers}
            
            # Extract body
            body = self._get_message_body(message['payload'])
            
            return {
                'message_id': msg_id,
                'thread_id': message.get('threadId'),
                'sender': header_dict.get('From', ''),
                'recipient': header_dict.get('To', ''),
                'subject': header_dict.get('Subject', ''),
                'date': header_dict.get('Date', ''),
                'body': body,
                'labels': message.get('labelIds', []),
                'snippet': message.get('snippet', ''),
                'has_attachments': 'parts' in message['payload']
            }
            
        except HttpError as error:
            print(f'Error fetching message {msg_id}: {error}')
            return None
    
    def _get_message_body(self, payload: dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        import base64
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
        else:
            # Simple message
            if 'data' in payload['body']:
                import base64
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8')
        
        return body
    
    def apply_label(self, message_id: str, label_name: str) -> bool:
        """
        Apply a label to a message.
        
        Args:
            message_id: Gmail message ID
            label_name: Label name to apply
        
        Returns:
            True if successful
        """
        try:
            # Get or create label
            label_id = self._get_or_create_label(label_name)
            
            # Apply label
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return True
            
        except HttpError as error:
            print(f'Error applying label: {error}')
            return False
    
    def _get_or_create_label(self, label_name: str) -> str:
        """Get label ID or create if doesn't exist"""
        try:
            # List existing labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Check if label exists
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
            
            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            return created_label['id']
            
        except HttpError as error:
            print(f'Error with label: {error}')
            raise
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark message as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error marking as read: {error}')
            return False
    
    def mark_as_important(self, message_id: str) -> bool:
        """Mark message as important (star it)"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['STARRED']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error marking as important: {error}')
            return False
    
    def archive_message(self, message_id: str) -> bool:
        """Archive message (remove from inbox)"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error archiving: {error}')
            return False
    
    def move_to_spam(self, message_id: str) -> bool:
        """Move message to spam"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['SPAM']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error moving to spam: {error}')
            return False


# Global client instance
_gmail_client = None


def get_gmail_client() -> GmailClient:
    """Get or create Gmail client singleton"""
    global _gmail_client
    if _gmail_client is None:
        _gmail_client = GmailClient()
    return _gmail_client


# LangChain Tools
@tool
def fetch_gmail_emails(max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch unread emails from Gmail.
    
    Args:
        max_results: Maximum number of emails to fetch
    
    Returns:
        List of email dictionaries
    """
    client = get_gmail_client()
    return client.fetch_unread_emails(max_results)


@tool
def apply_gmail_label(message_id: str, label_name: str) -> bool:
    """
    Apply a label to a Gmail message.
    
    Args:
        message_id: Gmail message ID
        label_name: Label name to apply
    
    Returns:
        True if successful
    """
    client = get_gmail_client()
    return client.apply_label(message_id, label_name)


@tool
def mark_gmail_important(message_id: str) -> bool:
    """
    Mark a Gmail message as important (star it).
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        True if successful
    """
    client = get_gmail_client()
    return client.mark_as_important(message_id)


@tool
def archive_gmail_message(message_id: str) -> bool:
    """
    Archive a Gmail message.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        True if successful
    """
    client = get_gmail_client()
    return client.archive_message(message_id)


@tool
def move_gmail_to_spam(message_id: str) -> bool:
    """
    Move a Gmail message to spam.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        True if successful
    """
    client = get_gmail_client()
    return client.move_to_spam(message_id)
