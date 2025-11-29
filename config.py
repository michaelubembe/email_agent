import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class EmailProvider(Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    IMAP = "imap"

class LLMProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

@dataclass
class AgentConfig:
    # Email Settings
    email_provider: EmailProvider
    email_address: str
    
    # Agent Settings
    llm_provider: LLMProvider
    llm_api_key: str

    # Optional Settings
    email_password: Optional[str] = None  # For App Passwords
    oauth_credentials_path: Optional[str] = None # For OAuth
    
    base_url: str = "http://localhost:8000"
    google_client_secrets_json: Optional[str] = None # Content of credentials.json for env var usage
    
    # Behavior
    auto_send: bool = False  # If False, saves as draft
    
    @classmethod
    def from_env(cls):
        # Simple default config based on user request
        return cls(
            email_provider=EmailProvider.GMAIL,
            email_address=os.getenv("EMAIL_ADDRESS", ""),
            oauth_credentials_path=os.getenv("GMAIL_CREDENTIALS", "credentials.json"),
            google_client_secrets_json=os.getenv("GOOGLE_CLIENT_SECRETS_JSON"),
            base_url=os.getenv("BASE_URL", "http://localhost:8000"),
            llm_provider=LLMProvider.GEMINI,
            llm_api_key=os.getenv("GEMINI_API_KEY", ""),
            auto_send=False # User requested Draft mode
        )
