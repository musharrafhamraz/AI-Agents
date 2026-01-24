"""Google Calendar API client."""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

from src.config import settings


# Scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarEventData:
    """Data class for calendar events."""

    def __init__(
        self,
        event_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
    ):
        self.event_id = event_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.location = location
        self.attendees = attendees or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "description": self.description,
            "location": self.location,
            "attendees": self.attendees,
        }


class GoogleCalendarClient:
    """Client for interacting with Google Calendar API."""

    def __init__(self) -> None:
        """Initialize the Google Calendar client."""
        self.credentials: Optional[Credentials] = None
        self.service = None
        self.token_file = Path("token.pickle")

    def authenticate(self) -> None:
        """
        Authenticate with Google Calendar API using OAuth 2.0.
        
        This will open a browser window for first-time authentication.
        Subsequent calls will use the saved token.
        """
        # Load existing credentials
        if self.token_file.exists():
            with open(self.token_file, 'rb') as token:
                self.credentials = pickle.load(token)

        # Refresh or get new credentials
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                # Create credentials dict for OAuth flow
                client_config = {
                    "installed": {
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                        "redirect_uris": [settings.google_redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                }
                
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                self.credentials = flow.run_local_server(port=8090)

            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)

        # Build the service
        self.service = build('calendar', 'v3', credentials=self.credentials)

    def _parse_datetime(self, dt_dict: Dict[str, Any]) -> datetime:
        """
        Parse datetime from Google Calendar API response.
        
        Args:
            dt_dict: Dictionary containing 'dateTime' or 'date'
            
        Returns:
            Parsed datetime object
        """
        if 'dateTime' in dt_dict:
            # Parse with timezone
            dt_str = dt_dict['dateTime']
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        elif 'date' in dt_dict:
            # All-day event, set to start of day
            date_str = dt_dict['date']
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return pytz.UTC.localize(dt)
        else:
            raise ValueError("Invalid datetime format in event")

    def fetch_upcoming_events(
        self,
        days_ahead: int = 7,
        calendar_id: Optional[str] = None
    ) -> List[CalendarEventData]:
        """
        Fetch upcoming events from Google Calendar.
        
        Args:
            days_ahead: Number of days to look ahead
            calendar_id: Calendar ID (defaults to primary)
            
        Returns:
            List of calendar events
        """
        if not self.service:
            self.authenticate()

        calendar_id = calendar_id or settings.google_calendar_id

        # Calculate time range
        now = datetime.utcnow().isoformat() + 'Z'
        time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=time_max,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            
            parsed_events = []
            for event in events:
                # Skip cancelled events
                if event.get('status') == 'cancelled':
                    continue

                event_data = CalendarEventData(
                    event_id=event['id'],
                    title=event.get('summary', 'No Title'),
                    start_time=self._parse_datetime(event['start']),
                    end_time=self._parse_datetime(event['end']),
                    description=event.get('description'),
                    location=event.get('location'),
                    attendees=[
                        {'email': attendee.get('email', ''), 'name': attendee.get('displayName', '')}
                        for attendee in event.get('attendees', [])
                    ]
                )
                parsed_events.append(event_data)

            return parsed_events

        except HttpError as error:
            raise Exception(f"Error fetching events: {error}")

    def sync_events(
        self,
        sync_token: Optional[str] = None,
        calendar_id: Optional[str] = None
    ) -> Tuple[List[CalendarEventData], Optional[str]]:
        """
        Sync events using incremental sync with sync tokens.
        
        Args:
            sync_token: Previous sync token for incremental sync
            calendar_id: Calendar ID (defaults to primary)
            
        Returns:
            Tuple of (events list, new sync token)
        """
        if not self.service:
            self.authenticate()

        calendar_id = calendar_id or settings.google_calendar_id

        try:
            if sync_token:
                # Incremental sync
                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    syncToken=sync_token
                ).execute()
            else:
                # Full sync - get events from now onwards
                now = datetime.utcnow().isoformat() + 'Z'
                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    timeMin=now,
                    maxResults=100,
                    singleEvents=True
                ).execute()

            events = events_result.get('items', [])
            new_sync_token = events_result.get('nextSyncToken')

            parsed_events = []
            for event in events:
                # Include cancelled events so we can mark them as deleted
                event_data = CalendarEventData(
                    event_id=event['id'],
                    title=event.get('summary', 'No Title'),
                    start_time=self._parse_datetime(event['start']) if 'start' in event else datetime.utcnow(),
                    end_time=self._parse_datetime(event['end']) if 'end' in event else datetime.utcnow(),
                    description=event.get('description'),
                    location=event.get('location'),
                    attendees=[
                        {'email': attendee.get('email', ''), 'name': attendee.get('displayName', '')}
                        for attendee in event.get('attendees', [])
                    ]
                )
                parsed_events.append(event_data)

            return parsed_events, new_sync_token

        except HttpError as error:
            if error.resp.status == 410:
                # Sync token expired, do full sync
                return self.sync_events(sync_token=None, calendar_id=calendar_id)
            raise Exception(f"Error syncing events: {error}")

    def get_event_by_id(
        self,
        event_id: str,
        calendar_id: Optional[str] = None
    ) -> Optional[CalendarEventData]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: Google Calendar event ID
            calendar_id: Calendar ID (defaults to primary)
            
        Returns:
            Calendar event data or None if not found
        """
        if not self.service:
            self.authenticate()

        calendar_id = calendar_id or settings.google_calendar_id

        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            if event.get('status') == 'cancelled':
                return None

            return CalendarEventData(
                event_id=event['id'],
                title=event.get('summary', 'No Title'),
                start_time=self._parse_datetime(event['start']),
                end_time=self._parse_datetime(event['end']),
                description=event.get('description'),
                location=event.get('location'),
                attendees=[
                    {'email': attendee.get('email', ''), 'name': attendee.get('displayName', '')}
                    for attendee in event.get('attendees', [])
                ]
            )

        except HttpError as error:
            if error.resp.status == 404:
                return None
            raise Exception(f"Error fetching event: {error}")
