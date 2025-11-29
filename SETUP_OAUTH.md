# Multi-User OAuth Setup Guide

Your email agent now supports multiple users! Each user can log in with their own Gmail account.

## Changes Made

1. **Multi-user authentication**: Users now log in with their Gmail accounts via OAuth
2. **Session management**: Each user's credentials are stored in their session
3. **Login/Logout UI**: Added Google Sign-In button and logout functionality
4. **Per-user email processing**: Each user's emails are processed using their own credentials

## Setup Instructions

### 1. Update Google Cloud Console Settings

Since users will now authenticate via a web flow, you need to update your OAuth redirect URI:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/api/auth/callback
   ```
6. Click **Save**

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Update your `.env` file:

```bash
EMAIL_ADDRESS=your-email@gmail.com  # Not used for auth anymore, but kept for config
GMAIL_CREDENTIALS=credentials.json
GEMINI_API_KEY=your-gemini-api-key
SECRET_KEY=your-secret-key-for-sessions  # Generate a random string
```

To generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run the Application

```bash
python app.py
```

Or with uvicorn:
```bash
uvicorn app:app --reload --port 8000
```

### 5. Using the Application

1. Open http://localhost:8000 in your browser
2. Click "Sign in with Google"
3. Authorize the application with your Gmail account
4. Once logged in, click "Check Emails & Draft Replies"
5. The agent will process your unread emails and create draft replies

## Security Notes

- User credentials are stored in memory (session storage)
- In production, you should:
  - Use a proper database to store user sessions
  - Use HTTPS for all connections
  - Set secure session cookie flags
  - Implement proper session expiration
  - Add CSRF protection

## Architecture

- **app.py**: Main FastAPI application with OAuth endpoints
- **email_client.py**: Gmail API client with per-user authentication
- **agent.py**: AI agent for generating email replies
- **templates/index.html**: Frontend with login/logout UI
- **static/script.js**: JavaScript for handling authentication flow
- **static/style.css**: Styling for the UI

## Troubleshooting

**Issue**: "Redirect URI mismatch" error
- **Solution**: Make sure you added `http://localhost:8000/api/auth/callback` to your Google Cloud Console OAuth settings

**Issue**: Users can't log in
- **Solution**: Check that your `credentials.json` file is present and valid

**Issue**: Session expires
- **Solution**: Currently sessions are stored in memory. Restart the server or implement persistent session storage.
