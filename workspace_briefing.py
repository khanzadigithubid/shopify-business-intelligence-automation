"""
Google Workspace Briefing Workflow - Main Orchestrator
Fetches calendar events, unread emails, and recent drive files using stored OAuth credentials,
then generates a clean executive briefing markdown file.
"""

import os
import json
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SECRETS_DIR = os.path.expanduser(r"~\.openclaw\secrets")
TOKEN_PATH = os.path.join(SECRETS_DIR, "google-workspace-token.json")
OUTPUT_DIR = os.path.expanduser(r"~\.openclaw\workspace\briefings")

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_credentials():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"OAuth token not found at {TOKEN_PATH}. Run bootstrap script first.")
    
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds and creds.expired and creds.refresh_token:
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
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
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
        
    print(f"Briefing successfully generated at: {filepath}")
    return filepath

if __name__ == "__main__":
    generate_briefing()
