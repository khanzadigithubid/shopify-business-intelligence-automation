# Shopify Business Intelligence Automation

A read-only Python workflow that fetches daily Shopify orders and current product inventory, calculates operational metrics, optionally asks an OpenAI-compatible model for aggregate insights, and writes a Markdown report that GitHub Actions can commit automatically.

## Workflow

```text
GitHub schedule (07:00 Asia/Karachi)
        -> Shopify Admin GraphQL API (read-only)
        -> Metrics and low-stock analysis
        -> Optional AI aggregate analysis
        -> shopify_reports/shopify-report-YYYY-MM-DD.md
        -> GitHub Actions commit and push
```

The workflow does not fetch customer names, emails, addresses, or raw message content. Reports contain aggregate metrics and product names only.

## Local setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r shopify_automation/requirements.txt
```

Set environment variables outside the repository:

```powershell
$env:SHOPIFY_STORE_DOMAIN = "your-store.myshopify.com"
$env:SHOPIFY_ACCESS_TOKEN = "***"
$env:SHOPIFY_API_VERSION = "2025-10"
$env:REPORT_TIMEZONE = "Asia/Karachi"
$env:LOW_STOCK_THRESHOLD = "10"
# Optional aggregate AI analysis:
$env:AI_API_KEY = "***"
$env:AI_BASE_URL = "https://openrouter.ai/api/v1"
$env:AI_MODEL = "openai/gpt-4o-mini"
```

Run against Shopify:

```bash
python -m shopify_automation --output-dir shopify_reports
```

The default report date is yesterday in `REPORT_TIMEZONE`, which avoids producing a partial current-day report. To rerun a specific day:

```bash
python -m shopify_automation --report-date 2026-08-09 --output-dir shopify_reports
```

Run the explicit development demo without any Shopify credentials:

```bash
python -m shopify_automation --demo --report-date 2026-08-09 --output-dir shopify_reports
```

Demo mode is never enabled by the GitHub workflow.

## Shopify access

Create a Shopify custom app or private app appropriate for the store and grant only the read scopes needed for products, inventory, orders, and shop information. Store the Admin API token in GitHub Actions Secrets. Do not commit tokens or `.env` files.

## GitHub Actions setup

The workflow is `.github/workflows/shopify-report.yml`.

Configure these repository secrets under **Settings -> Secrets and variables -> Actions -> Repository secrets**:

- `SHOPIFY_STORE_DOMAIN`
- `SHOPIFY_ACCESS_TOKEN`
- `AI_API_KEY` (optional)

---
*Managed by OpenClaw & ClawForge*
