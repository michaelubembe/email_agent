import google.generativeai as genai
from config import AgentConfig

class Agent:
    def __init__(self, config: AgentConfig):
        self.config = config
        genai.configure(api_key=self.config.llm_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_reply(self, email_content):
        """Generates a reply for the given email content."""
        # Extract sender name from email address
        sender = email_content.get('sender', 'Unknown')
        sender_name = sender
        
        # Try to extract name from "Name <email@example.com>" format
        if "<" in sender:
            sender_name = sender.split("<")[0].strip()
        # If no name found, use the part before @ in email
        elif "@" in sender:
            sender_name = sender.split("@")[0].strip()
        
        prompt = f"""
        You are a helpful professional email assistant. 
        Draft a comprehensive, professional, and respectful reply to the following email.
        
        CRITICAL INSTRUCTIONS:
        - Output ONLY the body of the email.
        - Do NOT include "Subject:" or "Body:" labels.
        - Do NOT include conversational filler like "Here is the draft".
        - Start with "Dear {sender_name},"
        - Write a comprehensive, professional, and respectful reply body.
        - End with "Kind regards,\\nLubembe Michael"
        - The reply should be well-structured and address all points in the original email.
        
        Sender: {email_content.get('sender')}
        Subject: {email_content.get('subject')}
        Body: {email_content.get('body')}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating reply: {e}")
            return "Error: Could not generate reply."
