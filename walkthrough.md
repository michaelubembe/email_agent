# Email Agent Walkthrough

This agent connects to your Gmail account, reads unread emails, and drafts replies using Gemini.

## Prerequisites

- Python 3.8+
- A Google Cloud Project with Gmail API enabled
- A Gemini API Key

## Setup Instructions

### 1. Install Dependencies

Run the following command to install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Open `.env` and fill in your details:
    -   `EMAIL_ADDRESS`: Your Gmail address.
    -   `GEMINI_API_KEY`: Get one from [Google AI Studio](https://aistudio.google.com/).
    -   `GMAIL_CREDENTIALS`: Path to your OAuth credentials file (default: `credentials.json`).

### 3. Google Cloud Setup (OAuth)

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Enable the **Gmail API**.
4.  Go to **APIs & Services > Credentials**.
5.  Create **OAuth 2.0 Client ID** credentials (Application type: **Desktop app**).
6.  Download the JSON file, rename it to `credentials.json`, and place it in the project root.
7.  **Important**: Add your email address as a **Test User** in the OAuth Consent Screen configuration.

## Running the Agent

Run the agent with:

```bash
python3 main.py
```

- On the first run, the agent will print a URL to the console.
- Open the URL in your browser and authorize the app.
- You will be redirected to a `localhost` page (which may fail to load).
- Copy the `code` parameter from the URL in your address bar.
- Paste the code back into the terminal.
- Once authorized, a `token.json` file will be created for future runs.
- The agent will check for unread emails and create drafts in your Gmail 'Drafts' folder.

## Verification

1.  Send an email to yourself (or have someone send one).
2.  Run the agent.
3.  Check your **Drafts** folder in Gmail. You should see a reply drafted by Gemini!
