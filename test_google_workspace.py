from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from pathlib import Path

TOKEN_FILE = Path(r"C:\Users\DELL\.openclaw\secrets\google-workspace-token.json")

def main():
    if not TOKEN_FILE.exists():
        print("Token file not found!")
        return

    data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes")
    )

    print("Testing Google Workspace APIs with stored token...\n")

    # 1. Calendar Test
    try:
        service = build('calendar', 'v3', credentials=creds)
        calendar_list = service.calendarList().list(maxResults=5).execute()
        print("[SUCCESS] Calendar API:")
        for cal in calendar_list.get('items', []):
            print(f"  - Calendar: {cal.get('summary')}")
    except Exception as e:
        print(f"[ERROR] Calendar API failed: {e}")

    # 2. Gmail Test
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=3).execute()
        messages = results.get('messages', [])
        print("\n[SUCCESS] Gmail API:")
        print(f"  Found {len(messages)} recent messages.")
    except Exception as e:
        print(f"[ERROR] Gmail API failed: {e}")

    # 3. Drive Test
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=3, fields="files(id, name)").execute()
        items = results.get('files', [])
        print("\n[SUCCESS] Drive API:")
        for item in items:
            print(f"  - File: {item.get('name')} ({item.get('id')})")
    except Exception as e:
        print(f"[ERROR] Drive API failed: {e}")

if __name__ == "__main__":
    main()
