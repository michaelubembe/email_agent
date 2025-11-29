import os
import secrets
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from config import AgentConfig
from email_client import EmailClient
from agent import Agent

# Load environment variables
load_dotenv()

app = FastAPI(title="Email Agent")

# Add session middleware with a secret key
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for user credentials (in production, use a database)
user_sessions = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main UI page."""
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/auth/status")
async def auth_status(request: Request):
    """Check if user is authenticated."""
    session_id = request.session.get("session_id")
    if session_id and session_id in user_sessions:
        user_info = user_sessions[session_id].get("user_info", {})
        return JSONResponse({
            "authenticated": True,
            "email": user_info.get("email", "Unknown")
        })
    return JSONResponse({"authenticated": False})

@app.get("/api/auth/login")
async def login(request: Request):
    """Initiate OAuth login flow."""
    try:
        config = AgentConfig.from_env()
        client = EmailClient(config, session_id=None)
        
        # Get authorization URL
        auth_url = client.get_auth_url()
        
        return JSONResponse({
            "auth_url": auth_url
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/callback")
async def auth_callback(request: Request, code: str = None, state: str = None):
    """Handle OAuth callback."""
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")
    
    try:
        config = AgentConfig.from_env()
        client = EmailClient(config, session_id=None)
        
        # Exchange code for credentials
        creds = client.handle_oauth_callback(code)
        
        # Get user info
        user_info = client.get_user_info(creds)
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        user_sessions[session_id] = {
            "credentials": creds,
            "user_info": user_info
        }
        
        # Set session cookie
        request.session["session_id"] = session_id
        
        # Redirect back to main page
        return RedirectResponse(url="/")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/logout")
async def logout(request: Request):
    """Logout user and clear session."""
    session_id = request.session.get("session_id")
    if session_id and session_id in user_sessions:
        del user_sessions[session_id]
    request.session.clear()
    return JSONResponse({"success": True})

@app.post("/api/process-emails")
async def process_emails(request: Request):
    """Process unread emails and create draft replies."""
    # Check authentication
    session_id = request.session.get("session_id")
    if not session_id or session_id not in user_sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Load config
        config = AgentConfig.from_env()
        
        # Get user credentials from session
        user_data = user_sessions[session_id]
        
        # Initialize components with user's credentials
        client = EmailClient(config, session_id=session_id, credentials=user_data["credentials"])
        agent = Agent(config)
        
        # Fetch unread emails
        emails = client.get_unread_emails()
        
        if not emails:
            return JSONResponse({
                'success': True,
                'message': 'No unread emails found.',
                'count': 0
            })
        
        # Process each email
        drafts_created = 0
        for email in emails:
            # Generate reply
            reply_body = agent.generate_reply(email)
            
            # Extract email address from sender
            sender_email = email['sender']
            if "<" in sender_email:
                sender_email = sender_email.split("<")[1].strip(">")
            
            # Create draft
            draft = client.create_draft(
                to_email=sender_email,
                subject=f"Re: {email['subject']}",
                body=reply_body
            )
            
            if draft:
                drafts_created += 1
        
        return JSONResponse({
            'success': True,
            'message': f'Successfully created {drafts_created} draft(s). Please check your Gmail inbox!',
            'count': drafts_created
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


