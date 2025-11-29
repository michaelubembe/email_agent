# Migration Checklist - Multi-User OAuth

## Quick Start

### 1. Update Google Cloud Console
- Add redirect URI: `http://localhost:8000/api/auth/callback`
- Location: Google Cloud Console > APIs & Services > Credentials > Your OAuth Client

### 2. Update .env file
Add this line to your `.env`:
```
SECRET_KEY=<generate-random-string>
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Install new dependency
```bash
pip install itsdangerous
```

### 4. Remove old token.json (optional)
The old single-user token is no longer needed:
```bash
rm token.json
```

### 5. Start the server
```bash
python app.py
```

### 6. Test it out
1. Visit http://localhost:8000
2. Click "Sign in with Google"
3. Authorize with any Gmail account
4. Process emails!

## What Changed

- ✅ Multi-user support - anyone can log in with their Gmail
- ✅ OAuth web flow - no more manual token entry
- ✅ Session management - each user has their own session
- ✅ Login/Logout UI - clean authentication interface
- ✅ Per-user credentials - each user's emails are private

## Notes

- Sessions are stored in memory (restart clears all sessions)
- For production, use a database for session storage
- Each user authenticates with their own Gmail account
- No shared credentials between users
