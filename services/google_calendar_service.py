"""
Google Calendar Service for Barber Manager.
Handles OAuth 2.0 authentication and API interactions.
"""
import os.path
import datetime
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    """
    Service for interacting with Google Calendar API.
    """
    
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.error = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.
        
        Returns:
            True if authentication was successful, False otherwise.
        """
        self.creds = None
        self.error = None
        
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.TOKEN_FILE):
            try:
                self.creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, SCOPES)
            except Exception as e:
                self.error = f"Error loading token: {str(e)}"
                os.remove(self.TOKEN_FILE)  # Corrupt token, remove it

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    self.error = f"Error refreshing token: {str(e)}"
                    return False
            else:
                if not os.path.exists(self.CREDENTIALS_FILE):
                    self.error = f"Archivo {self.CREDENTIALS_FILE} no encontrado."
                    return False
                    
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.CREDENTIALS_FILE, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    self.error = f"Error during auth flow: {str(e)}"
                    return False
                    
            # Save the credentials for the next run
            try:
                with open(self.TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            except Exception as e:
                self.error = f"Error saving token: {str(e)}"
                return False

        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            self.error = f"Error building service: {str(e)}"
            return False

    def is_authenticated(self) -> bool:
        """Check if we have valid credentials loaded."""
        if not self.creds or not self.service:
             # Try to load existing token silently
            if os.path.exists(self.TOKEN_FILE):
                try:
                    self.creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, SCOPES)
                    if self.creds and self.creds.valid:
                        self.service = build('calendar', 'v3', credentials=self.creds)
                        return True
                    elif self.creds and self.creds.expired and self.creds.refresh_token:
                        # Attempt silent refresh
                        try:
                            self.creds.refresh(Request())
                            self.service = build('calendar', 'v3', credentials=self.creds)
                            return True
                        except:
                            pass
                except:
                    pass
            return False
            
        return True

    def get_calendars(self) -> List[Dict[str, str]]:
        """Get list of available calendars."""
        if not self.is_authenticated():
            return []
            
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            result = []
            for cal in calendars:
                # Filter out some generic calendars if needed, or keeping all writable ones
                if cal.get('accessRole') in ['owner', 'writer']:
                    result.append({
                        'id': cal['id'],
                        'summary': cal.get('summary', 'Sin nombre'),
                        'primary': cal.get('primary', False)
                    })
            return result
        except HttpError as error:
            self.error = f"An error occurred: {error}"
            return []

    def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> str:
        """
        Create a new event in Google Calendar.
        
        Args:
            calendar_id: ID of the calendar to create event in
            event_data: Dictionary with event details
            
        Returns:
            ID of the created event or None if failed
        """
        if not self.is_authenticated():
            return None
            
        try:
            event = self.service.events().insert(calendarId=calendar_id, body=event_data).execute()
            return event.get('id')
        except HttpError as error:
            self.error = f"Error creating event: {error}"
            print(f"Google Calendar API Error: {error}")
            return None

    def update_event(self, calendar_id: str, event_id: str, event_data: Dict[str, Any]) -> bool:
        """
        Update an existing event.
        
        Args:
            calendar_id: Calendar ID
            event_id: Event ID to update
            event_data: New event details
            
        Returns:
            True if successful
        """
        if not self.is_authenticated():
            try:
                 if not self.authenticate(): # Try force auth/refresh if strictly needed or rely on stored token
                     return False
            except:
                return False

        try:
            self.service.events().update(
                calendarId=calendar_id, 
                eventId=event_id, 
                body=event_data
            ).execute()
            return True
        except HttpError as error:
            if error.resp.status == 404:
                # Event not found, maybe deleted in calendar manually
                return False
            self.error = f"Error updating event: {error}"
            print(f"Google Calendar API Error: {error}")
            return False

    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """
        Delete an event.
        
        Args:
            calendar_id: Calendar ID
            event_id: Event ID to delete
            
        Returns:
            True if successful
        """
        if not self.is_authenticated():
             # Basic check, real implementation might try to re-auth
             pass

        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return True
        except HttpError as error:
            if error.resp.status == 404:
                # Already deleted
                return True
            if error.resp.status == 410:
                # Gone
                return True
                
            self.error = f"Error deleting event: {error}"
            print(f"Google Calendar API Error: {error}")
            return False
            
    def get_last_error(self) -> str:
        return self.error
