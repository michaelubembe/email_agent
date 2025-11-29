import unittest
from unittest.mock import MagicMock, patch
from config import AgentConfig, EmailProvider, LLMProvider
from email_client import EmailClient
from agent import Agent

class TestEmailAgent(unittest.TestCase):
    def setUp(self):
        self.config = AgentConfig(
            email_provider=EmailProvider.GMAIL,
            email_address="test@example.com",
            oauth_credentials_path="dummy.json",
            llm_provider=LLMProvider.GEMINI,
            llm_api_key="dummy_key",
            auto_send=False
        )

    @patch('email_client.build')
    @patch('email_client.InstalledAppFlow')
    @patch('email_client.Credentials')
    @patch('os.path.exists')
    def test_email_client_init(self, mock_exists, mock_creds, mock_flow, mock_build):
        # Mock credentials existence
        mock_exists.return_value = True
        
        client = EmailClient(self.config)
        self.assertIsNotNone(client.service)

    @patch('email_client.build')
    @patch('email_client.InstalledAppFlow')
    @patch('email_client.Credentials')
    @patch('os.path.exists')
    def test_get_unread_emails(self, mock_exists, mock_creds, mock_flow, mock_build):
        mock_exists.return_value = True
        
        # Mock service response
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_messages = {
            "messages": [{"id": "123"}]
        }
        mock_service.users().messages().list().execute.return_value = mock_messages
        
        mock_message_detail = {
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"}
                ]
            },
            "snippet": "Test Body"
        }
        mock_service.users().messages().get().execute.return_value = mock_message_detail
        
        client = EmailClient(self.config)
        emails = client.get_unread_emails()
        
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['subject'], "Test Subject")
        self.assertEqual(emails[0]['sender'], "sender@example.com")

    @patch('agent.genai')
    def test_agent_generate_reply(self, mock_genai):
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.return_value.text = "This is a reply."
        
        agent = Agent(self.config)
        reply = agent.generate_reply({"sender": "foo", "subject": "bar", "body": "baz"})
        
        self.assertEqual(reply, "This is a reply.")

if __name__ == '__main__':
    unittest.main()
