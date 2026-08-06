"""Strict, read-only Google Workspace OAuth bootstrap for the local AI Employee host.

This script intentionally requests exactly three scopes and rejects/revokes any
OAuth result that contains an additional scope.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode

import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

CLIENT_FILE = Path(r"C:\Users\DELL\.openclaw\secrets\google-workspace-client.json")
TOKEN_FILE = Path(r"C:\Users\DELL\.openclaw\secrets\google-workspace-token.json")

# DO NOT add scopes here without first explicitly approving them with the user.
EXPECTED_SCOPES = {
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
}


def revoke(access_token: str) -> None:
    try:
        requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": access_token},
            timeout=15,
        )
    except requests.RequestException:
        pass


def token_scopes(access_token: str) -> set[str]:
    response = requests.get(
        "https://oauth2.googleapis.com/tokeninfo",
        params={"access_token": access_token},
        timeout=15,
    )
    response.raise_for_status()
    raw = response.json().get("scope", "")
    return set(raw.split())


def fail_with_extra_scopes(actual: set[str], access_token: str | None = None) -> None:
    extra = sorted(actual - EXPECTED_SCOPES)
    missing = sorted(EXPECTED_SCOPES - actual)
    if access_token:
        revoke(access_token)
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
    print("\nSTOP: OAuth did not produce exactly the approved read-only scopes.")
    if extra:
        print("Unexpected scopes:")
        for scope in extra:
            print(f"  - {scope}")
    if missing:
        print("Missing requested scopes:")
        for scope in missing:
            print(f"  - {scope}")
    print("The token was revoked/deleted. Do not continue until the consent configuration is corrected.")
    raise SystemExit(2)


def main() -> None:
    if not CLIENT_FILE.is_file():
        raise SystemExit(f"Missing OAuth client file: {CLIENT_FILE}")
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("The browser will request EXACTLY these scopes:")
    for scope in sorted(EXPECTED_SCOPES):
        print(f"  - {scope}")
    print("\nSTOP before clicking Allow if the consent page mentions any other permission, including send, modify, delete, create, share, contacts, profile, or account-management access.")
    input("When you are ready to open the consent page, press Enter (or Ctrl+C to cancel): ")

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_FILE),
        scopes=sorted(EXPECTED_SCOPES),
    )
    # A random localhost port is used; the Desktop OAuth client accepts localhost.
    credentials = flow.run_local_server(
        host="localhost",
        port=0,
        authorization_prompt_message="Open this URL in your browser if it does not open automatically:\n{url}\n",
        success_message="Authorization completed. You may close this browser tab.",
        access_type="offline",
        prompt="consent",
        include_granted_scopes="false",
    )

    access_token = credentials.token
    actual = token_scopes(access_token)
    if actual != EXPECTED_SCOPES:
        fail_with_extra_scopes(actual, access_token)

    # Save only after exact scope validation succeeds.
    TOKEN_FILE.write_text(
        json.dumps(
            {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": sorted(actual),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nSUCCESS: exact read-only scopes granted and verified.")
    print(f"Token saved locally at: {TOKEN_FILE}")
    print("No token was copied into the cage workspace.")


if __name__ == "__main__":
    main()
