# Shopify Business Intelligence Automation

[![Generate Shopify Business Report](https://github.com/khanzadigithubid/shopify-business-intelligence-automation/actions/workflows/shopify-report.yml/badge.svg?branch=master)](https://github.com/khanzadigithubid/shopify-business-intelligence-automation/actions/workflows/shopify-report.yml)

A read-only Shopify business intelligence workflow that generates a daily Markdown report from Shopify order and inventory data. It calculates operational metrics, highlights low-stock products, and can optionally use an OpenAI-compatible model for aggregate business analysis.

> **Privacy-first:** The workflow does not request or report customer names, email addresses, shipping addresses, or message content. Reports contain aggregate metrics and product names only.

## What it does

- Fetches orders for a selected local business day through the Shopify Admin GraphQL API.
- Fetches the current product inventory snapshot.
- Excludes cancelled orders from sales and order metrics.
- Calculates sales, order count, average order value, fulfilment count, and cancelled orders.
- Lists the top products by units sold.
- Flags active products at or below the configured low-stock threshold.
- Uses deterministic analysis by default.
- Optionally sends aggregate metrics only to an OpenAI-compatible API such as OpenRouter.
- Generates `shopify_reports/shopify-report-YYYY-MM-DD.md`.
- Runs automatically through GitHub Actions and commits changed reports back to this repository.

## Architecture

```text
GitHub Actions schedule or manual run
                |
                v
       Python 3.12 application
                |
                v
  Shopify Admin GraphQL API (read-only)
                |
                +--> Orders for the report date
                +--> Current product inventory
                |
                v
       Metrics and business analysis
                |
                +--> Deterministic rules
                +--> Optional aggregate AI analysis
                |
                v
   shopify_reports/shopify-report-YYYY-MM-DD.md
                |
                v
       Git commit and push by Actions
```

## Repository structure

```text
.github/workflows/shopify-report.yml  # Scheduled and manual GitHub Actions workflow
shopify_automation/                   # Python package
  analyzer.py                         # Metrics and optional AI analysis
  config.py                           # Environment configuration
  demo_data.py                         # Local demo snapshot
  main.py                              # CLI and report orchestration
  models.py                            # Typed data models
  report.py                            # Markdown report renderer
  shopify_client.py                    # Read-only Shopify GraphQL client
  requirements.txt                     # Python dependencies
  test_automation.py                   # Unit tests
shopify_reports/                      # Generated Markdown reports
```

## GitHub Actions workflow

The workflow is defined in `.github/workflows/shopify-report.yml`.

- **Schedule:** Daily at 07:00 Pakistan Standard Time (PKT).
- **Cron:** `0 2 * * *` UTC, because GitHub Actions cron uses UTC.
- **Manual run:** Open **Actions → Generate Shopify Business Report → Run workflow**.
- **Manual date:** An optional `YYYY-MM-DD` date can be provided when starting a run.
- **Runtime:** Python 3.12 on an Ubuntu GitHub-hosted runner.
- **Permissions:** `contents: write`, required only so the workflow can commit generated reports.
- **Concurrency:** Only one report generation run is allowed at a time.

The normal scheduled run uses yesterday's date in `REPORT_TIMEZONE`, preventing a partial report for the current day.

## Configuration

Add the following under **Settings → Secrets and variables → Actions**.

### Required repository secrets

| Name | Purpose |
| --- | --- |
| `SHOPIFY_STORE_DOMAIN` | Store domain, for example `your-store.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN` | Shopify Admin API access token |

### Optional repository secrets

| Name | Purpose |
| --- | --- |
| `AI_API_KEY` | Enables optional aggregate AI analysis |

### Optional repository variables

| Name | Default | Purpose |
| --- | --- | --- |
| `SHOPIFY_API_VERSION` | `2025-10` | Shopify Admin API version |
| `AI_BASE_URL` | `https://openrouter.ai/api/v1` | OpenAI-compatible API base URL |
| `AI_MODEL` | `openai/gpt-4o-mini` | Model used for aggregate analysis |
| `REPORT_TIMEZONE` | `Asia/Karachi` | Local timezone used for report dates |
| `LOW_STOCK_THRESHOLD` | `10` | Inventory level at or below which products are flagged |

The Shopify custom app should have only the read scopes needed for shop information, orders, products, and inventory. Never commit tokens, `.env` files, OAuth credentials, or API keys.

## Run locally

### 1. Create an environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r shopify_automation/requirements.txt
```

### 3. Configure Shopify credentials

PowerShell:

```powershell
$env:SHOPIFY_STORE_DOMAIN = "your-store.myshopify.com"
$env:SHOPIFY_ACCESS_TOKEN = "your-read-only-token"
$env:REPORT_TIMEZONE = "Asia/Karachi"
$env:LOW_STOCK_THRESHOLD = "10"
```

Linux/macOS:

```bash
export SHOPIFY_STORE_DOMAIN="your-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="your-read-only-token"
export REPORT_TIMEZONE="Asia/Karachi"
export LOW_STOCK_THRESHOLD="10"
```

### 4. Generate a live report

```bash
python -m shopify_automation --output-dir shopify_reports
```

By default, the command reports on yesterday in the configured timezone. To generate a specific report date:

```bash
python -m shopify_automation \
  --report-date 2026-08-09 \
  --output-dir shopify_reports
```

### 5. Run the demo without Shopify credentials

```bash
python -m shopify_automation \
  --demo \
  --report-date 2026-08-09 \
  --output-dir shopify_reports
```

Demo mode uses local sample data and is never enabled by the production GitHub Actions workflow.

## Optional AI analysis

AI analysis is disabled unless `AI_API_KEY` is configured. When enabled, the application sends only aggregate values:

- Order count
- Sales total and currency
- Average order value
- Fulfilled and cancelled order counts
- Top product names and quantities
- Low-stock product names

The model is instructed to return short JSON arrays for highlights, recommendations, and risks. If the AI request fails or returns invalid data, the workflow safely falls back to deterministic analysis.

## Test locally

Run the package tests from the repository root:

```bash
python -m unittest shopify_automation.test_automation -v
```

The tests cover cancelled-order exclusion, aggregate report content, and low-stock alerts.

## Report output

Generated reports include:

- Executive summary
- Sales and order metrics
- Average order value
- Fulfilment and cancellation counts
- Top products by units sold
- Low-stock alerts
- Operational recommendations
- Risks requiring review
- Report scope and data-access notes

Example output: [`shopify_reports/shopify-report-2026-08-09.md`](shopify_reports/shopify-report-2026-08-09.md)

## Security and privacy

- Shopify access is read-only at the application level.
- Customer PII is not requested by the GraphQL queries.
- Secrets are loaded through environment variables or GitHub Actions Secrets.
- Generated reports are committed to the public repository by design; review report contents before enabling public reporting for a real store.
- Keep this repository private if product names, sales figures, or inventory levels are commercially sensitive.

## Limitations

- The workflow is a daily report generator, not a real-time event stream.
- Sales are based on the order totals returned by Shopify for the selected date.
- Inventory is a current snapshot, not historical inventory at the report date.
- Pagination is supported, while advanced segmentation and historical inventory tracking are outside the current scope.

---

Maintained by **Khanzadi Wazir Ali** with **ClawForge**.
