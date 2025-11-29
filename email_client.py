import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import AgentConfig

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose"
]

class EmailClient:
    def __init__(self, config: AgentConfig, session_id=None, credentials=None):
        self.config = config
        self.session_id = session_id
        self.credentials = credentials
        self.flow = None
        
        # Only authenticate if credentials are provided
        if credentials:
            self.service = self._build_service(credentials)
        else:
            self.service = None

    def _build_service(self, creds):
        """Build Gmail service with credentials."""
        try:
            # Refresh credentials if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            service = build("gmail", "v1", credentials=creds)
            return service
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def get_auth_url(self):
        """Get OAuth authorization URL for web flow."""
        if not os.path.exists(self.config.oauth_credentials_path):
            raise FileNotFoundError(f"Credentials file not found at {self.config.oauth_credentials_path}")
        
        self.flow = InstalledAppFlow.from_client_secrets_file(
            self.config.oauth_credentials_path, SCOPES
        )
        # Use the callback URL for web flow
        self.flow.redirect_uri = 'http://localhost:8000/api/auth/callback'
        
        auth_url, _ = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url
    
    def handle_oauth_callback(self, code):
        """Handle OAuth callback and exchange code for credentials."""
        if not os.path.exists(self.config.oauth_credentials_path):
            raise FileNotFoundError(f"Credentials file not found at {self.config.oauth_credentials_path}")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.config.oauth_credentials_path, SCOPES
        )
        flow.redirect_uri = 'http://localhost:8000/api/auth/callback'
        
        # Exchange authorization code for credentials
        flow.fetch_token(code=code)
        
        return flow.credentials
    
    def get_user_info(self, creds):
        """Get user email address from credentials."""
        try:
            service = build("gmail", "v1", credentials=creds)
            profile = service.users().getProfile(userId="me").execute()
            return {
                "email": profile.get("emailAddress", "Unknown")
            }
        except HttpError as error:
            print(f"An error occurred: {error}")
            return {"email": "Unknown"}

    def get_unread_emails(self, max_results=5):
        """Fetches unread emails from the inbox."""
        try:
            results = self.service.users().messages().list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results).execute()
            messages = results.get("messages", [])
            
            email_data = []
            for msg in messages:
                txt = self.service.users().messages().get(userId="me", id=msg["id"]).execute()
                payload = txt['payload']
                headers = payload['headers']
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
                snippet = txt.get('snippet', '')
                
                # Simple body extraction (can be improved for HTML/Multipart)
                body = snippet 
                
                email_data.append({
                    "id": msg["id"],
                    "subject": subject,
                    "sender": sender,
                    "body": body,
                    "snippet": snippet
                })
            return email_data

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def create_draft(self, to_email, subject, body):
        """Creates a draft email."""
        try:
            message = EmailMessage()
            message.set_content(body)
            message["To"] = to_email
            message["Subject"] = subject
            # message["From"] = self.config.email_address # Gmail API sets this automatically

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {
                "message": {
                    "raw": encoded_message
                }
            }
            
            draft = self.service.users().drafts().create(userId="me", body=create_message).execute()
            print(f"Draft id: {draft['id']} created.")
            return draft

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
