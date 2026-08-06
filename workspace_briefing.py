"""
Google Workspace Briefing Workflow - Main Orchestrator
Fetches calendar events, unread emails, and recent drive files using stored OAuth credentials,
then generates a clean executive briefing markdown file.
"""

import os
import json
import datetime
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Use platform-independent paths so the same workflow works locally on
# Windows and on GitHub-hosted Linux runners.
SECRETS_DIR = Path.home() / ".openclaw" / "secrets"
TOKEN_PATH = SECRETS_DIR / "google-workspace-token.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "briefings"

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_credentials():
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(f"OAuth token not found at {TOKEN_PATH}. Run bootstrap script first.")

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    # Always refresh when a refresh token is available. Access tokens normally
    # expire after about one hour, and the token file used by CI may not contain
    # an expiry timestamp. This keeps scheduled GitHub Actions runs reliable.
    if creds and creds.refresh_token:
        creds.refresh(Request())
    return creds

def fetch_calendar_events(service):
    try:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=5, singleEvents=True,
            orderBy='startTime').execute()
        return events_result.get('items', [])
    except Exception as e:
        return [{"summary": f"Error fetching calendar: {str(e)}"}]

def fetch_gmail_messages(service):
    try:
        results = service.users().messages().list(userId='me', q='is:unread', maxResults=5).execute()
        messages = results.get('messages', [])
        summaries = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
            headers = {h['name']: h['value'] for h in txt['payload']['headers']}
            summaries.append({
                "subject": headers.get('Subject', 'No Subject'),
                "from": headers.get('From', 'Unknown Sender')
            })
        return summaries
    except Exception as e:
        return [{"subject": f"Error fetching gmail: {str(e)}", "from": "System"}]

def fetch_drive_files(service):
    try:
        results = service.files().list(
            pageSize=5,
            fields="files(id, name, modifiedTime, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        return [{"name": f"Error fetching drive files: {str(e)}"}]

def generate_briefing():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    creds = get_credentials()
    
    cal_service = build('calendar', 'v3', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    events = fetch_calendar_events(cal_service)
    emails = fetch_gmail_messages(gmail_service)
    files = fetch_drive_files(drive_service)
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    markdown = f"""# Executive Workspace Briefing
Generated: {today_str}

## 📅 Upcoming Calendar Events
"""
    if events:
        for ev in events:
            start = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date', 'TBD'))
            markdown += f"- **{ev.get('summary', 'Untitled Event')}** ({start})\n"
    else:
        markdown += "- No upcoming events found.\n"

    markdown += "\n## ✉️ Unread Gmail Messages\n"
    if emails:
        for em in emails:
            markdown += f"- **{em.get('subject')}** — *from {em.get('from')}*\n"
    else:
        markdown += "- No unread messages.\n"

    markdown += "\n## 📁 Recently Modified Drive Files\n"
    if files:
        for f in files:
            markdown += f"- [{f.get('name')}]({f.get('webViewLink', '#')})\n"
    else:
        markdown += "- No recent files found.\n"

    filename = datetime.datetime.now().strftime("briefing-%Y-%m-%d.md")
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
        
    print(f"Briefing successfully generated at: {filepath}")
    return filepath

if __name__ == "__main__":
    generate_briefing()
