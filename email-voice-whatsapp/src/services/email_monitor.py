from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List, Dict, Optional
import base64
import logging

logger = logging.getLogger(__name__)


class EmailMonitorService:
    """Service for monitoring and fetching emails from Gmail"""
    
    def __init__(self, credentials: Dict):
        """Initialize with user's Gmail credentials"""
        self.creds = Credentials(
            token=credentials.get('token'),
            refresh_token=credentials.get('refresh_token'),
            token_uri=credentials.get('token_uri'),
            client_id=credentials.get('client_id'),
            client_secret=credentials.get('client_secret'),
            scopes=credentials.get('scopes')
        )
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def fetch_unread_emails(self, max_results: int = 10) -> List[Dict]:
        """Fetch unread emails from Gmail"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No unread emails found")
                return []
            
            emails = []
            for msg in messages:
                try:
                    email_data = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    parsed_email = self._parse_email(email_data)
                    if parsed_email:
                        emails.append(parsed_email)
                except Exception as e:
                    logger.error(f"Error fetching email {msg['id']}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(emails)} unread emails")
            return emails
            
        except Exception as e:
            logger.error(f"Failed to fetch emails: {str(e)}")
            raise Exception(f"Failed to fetch emails: {str(e)}")
    
    def _parse_email(self, email_data: Dict) -> Optional[Dict]:
        """Parse Gmail API response into structured format"""
        try:
            headers = {h['name']: h['value'] for h in email_data['payload']['headers']}
            
            # Get email body
            body = self._get_email_body(email_data['payload'])
            
            return {
                'id': email_data['id'],
                'sender': headers.get('From', 'Unknown'),
                'subject': headers.get('Subject', 'No Subject'),
                'body': body,
                'date': headers.get('Date', ''),
                'snippet': email_data.get('snippet', '')
            }
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            return None
    
    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        try:
            # Check if email has parts (multipart)
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    # Recursively check nested parts
                    elif 'parts' in part:
                        body = self._get_email_body(part)
                        if body:
                            return body
            
            # Single part email
            elif 'body' in payload:
                data = payload['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            return ''
        except Exception as e:
            logger.error(f"Error extracting email body: {str(e)}")
            return ''
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False
