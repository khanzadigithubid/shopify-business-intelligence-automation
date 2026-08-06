# AI Employee Workspace Backup

This repository contains the backup of the personal AI Agent workspace and configuration for **ClawForge** (Senior AI Engineering Partner) running inside **OpenClaw**.

## Purpose

- **Continuity**: Preserves standing preferences, custom system prompts, developer profile, and memory across agent sessions.
- **Automation & Scheduling**: Stores schedule manifests and task hooks.
- **Integration Scripts & Automations**: Houses helper scripts and automated workflows (e.g., Google Workspace OAuth setup, API testing, and Executive Briefing generation).

## Repository Structure

```text
├── .agents/            # Agent skills and extensions
├── memory/             # Daily engineering logs and notes
├── briefings/          # Generated executive workspace briefings
├── schedules/          # Task and cron manifests
├── AGENTS.md           # Workspace operating instructions
├── IDENTITY.md         # Agent identity & role definition
├── MEMORY.md           # Curated long-term memory & standing preferences
├── SOUL.md             # Persona, tone, and core principles
├── TOOLS.md            # Local environment notes & tool configurations
├── USER.md             # Developer profile & primary technology stack
├── google_workspace_oauth.py # Google Workspace OAuth utility & authentication flow
├── test_google_workspace.py  # API connectivity verification suite
└── workspace_briefing.py     # Automated Google Workspace Executive Briefing generator
```

## Google Workspace Briefing Workflow

The **Google Workspace Briefing Workflow** (`workspace_briefing.py`) is an automated integration script designed to consolidate key daily activities and productivity data from Google Workspace into a single, polished executive markdown briefing.

### Key Features
- **Google Calendar Integration**: Fetches upcoming scheduled events to highlight key meetings and time-bound commitments.
- **Gmail Integration**: Scans unread messages to surface urgent communications and sender details.
- **Google Drive Integration**: Retrieves recently modified files for quick access and tracking.
- **Executive Output**: Generates cleanly formatted markdown reports saved directly to the `briefings/` directory with timestamps.

### Utility Scripts
- `google_workspace_oauth.py`: Manages secure OAuth authentication and token lifecycle.
- `test_google_workspace.py`: Validates API scopes and connectivity across Calendar, Gmail, and Drive services.

### GitHub Actions Automation

The repository includes `.github/workflows/briefing.yml`. It can be started manually from the **Actions** tab or runs automatically every day at **06:00 Asia/Karachi**. The workflow:

1. Creates a clean Python environment on GitHub-hosted infrastructure.
2. Loads Google OAuth values from GitHub Actions Secrets without committing them to the repository.
3. Refreshes the Google access token using the read-only refresh token.
4. Fetches Calendar, Gmail, and Drive data through the official APIs.
5. Saves the generated report under `briefings/` and commits only that report back to GitHub.

Required repository secrets under **Settings → Secrets and variables → Actions**:

| Secret name | Value source |
| --- | --- |
| `GOOGLE_CLIENT_ID` | `client_id` in `google-workspace-token.json` |
| `GOOGLE_CLIENT_SECRET` | `client_secret` in `google-workspace-token.json` |
| `GOOGLE_ACCESS_TOKEN` | `token` in `google-workspace-token.json` |
| `GOOGLE_REFRESH_TOKEN` | `refresh_token` in `google-workspace-token.json` |

The access token is short-lived; the refresh token is what makes scheduled runs continue working. Never commit either token or the client secret to GitHub source files.

---
*Managed by OpenClaw & ClawForge*
