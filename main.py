import os
from dotenv import load_dotenv
from config import AgentConfig
from email_client import EmailClient
from agent import Agent

def main():
    # Load environment variables
    load_dotenv()
    
    # Load config
    config = AgentConfig.from_env()
    
    print(f"Starting Email Agent...")
    print(f"Provider: {config.email_provider.value}")
    print(f"LLM: {config.llm_provider.value}")
    print(f"Mode: {'Auto-Send' if config.auto_send else 'Draft'}")

    # Initialize components
    client = EmailClient(config)
    agent = Agent(config)
    
    # Fetch unread emails
    print("\nChecking for unread emails...")
    emails = client.get_unread_emails()
    
    if not emails:
        print("No unread emails found.")
        return

    print(f"Found {len(emails)} unread emails.")
    
    for email in emails:
        print(f"\nProcessing email from: {email['sender']}")
        print(f"Subject: {email['subject']}")
        
        # Generate reply
        print("Generating reply...")
        reply_body = agent.generate_reply(email)
        
        # Create draft
        print("Creating draft...")
        # Extract email address from sender string (simple logic, might need regex for complex cases)
        sender_email = email['sender'] 
        if "<" in sender_email:
            sender_email = sender_email.split("<")[1].strip(">")
            
        client.create_draft(to_email=sender_email, subject=f"Re: {email['subject']}", body=reply_body)
        print("Draft created successfully.")

if __name__ == "__main__":
    main()
