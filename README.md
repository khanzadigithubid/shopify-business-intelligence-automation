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

---
*Managed by OpenClaw & ClawForge*
