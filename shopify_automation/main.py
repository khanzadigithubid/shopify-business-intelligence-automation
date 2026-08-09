"""CLI entrypoint for the daily Shopify report."""

import argparse
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .analyzer import ai_analysis, calculate_metrics, deterministic_analysis
from .config import Settings
from .demo_data import build_demo_snapshot
from .models import StoreSnapshot
from .report import render_report
from .shopify_client import ShopifyClient


def _report_date(settings: Settings, override: str | None) -> date:
    if override:
        return date.fromisoformat(override)
    return datetime.now(ZoneInfo(settings.timezone)).date() - timedelta(days=1)


def _utc_bounds(day: date, timezone_name: str) -> tuple[datetime, datetime]:
    zone = ZoneInfo(timezone_name)
    start = datetime.combine(day, time.min, tzinfo=zone)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=zone)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def build_snapshot(settings: Settings, day: date, demo: bool) -> StoreSnapshot:
    if demo:
        return build_demo_snapshot()
    settings.require_shopify()
    assert settings.store_domain and settings.access_token
    client = ShopifyClient(settings.store_domain, settings.access_token, settings.api_version, settings.request_timeout_seconds)
    start, end = _utc_bounds(day, settings.timezone)
    return StoreSnapshot(client.get_shop_name(), client.fetch_orders(start, end), client.fetch_products())


def run(report_date: str | None, output_dir: str, demo: bool = False) -> Path:
    settings = Settings.from_env()
    day = _report_date(settings, report_date)
    snapshot = build_snapshot(settings, day, demo)
    metrics = calculate_metrics(snapshot, settings.low_stock_threshold)
    analysis = (
        ai_analysis(metrics, settings.ai_api_key, settings.ai_base_url, settings.ai_model, settings.request_timeout_seconds)
        if settings.ai_api_key and not demo
        else deterministic_analysis(metrics)
    )
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"shopify-report-{day.isoformat()}.md"
    path.write_text(render_report(day, snapshot, metrics, analysis), encoding="utf-8")
    print(f"Shopify report generated: {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a read-only Shopify business report.")
    parser.add_argument("--report-date", help="Local report date in YYYY-MM-DD format; defaults to yesterday.")
    parser.add_argument("--output-dir", default="shopify_reports")
    parser.add_argument("--demo", action="store_true", help="Use local demo data; never use in production CI.")
    args = parser.parse_args()
    run(args.report_date, args.output_dir, args.demo)


if __name__ == "__main__":
    main()

