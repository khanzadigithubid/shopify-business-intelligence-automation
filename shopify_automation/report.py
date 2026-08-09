"""Markdown report rendering."""

from datetime import date

from .models import Analysis, Metrics, StoreSnapshot


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render_report(report_date: date, snapshot: StoreSnapshot, metrics: Metrics, analysis: Analysis) -> str:
    lines = [
        f"# Shopify Daily Business Report — {report_date.isoformat()}",
        "",
        f"**Store:** {_escape(snapshot.store_name)}  ",
        f"**Analysis source:** {_escape(analysis.source)}  ",
        "",
        "> This report contains aggregated business metrics only. No customer PII is included.",
        "",
        "## Executive Summary",
        "",
        f"- **Sales:** {metrics.currency} {metrics.gross_sales}",
        f"- **Orders:** {metrics.order_count}",
        f"- **Average order value:** {metrics.currency} {metrics.average_order_value}",
        f"- **Fulfilled orders:** {metrics.fulfilled_orders}",
        f"- **Cancelled orders:** {metrics.cancelled_orders}",
        "",
        "## Highlights",
        "",
    ]
    lines.extend(f"- {_escape(item)}" for item in analysis.highlights or ("No highlights available.",))
    lines.extend(["", "## Top Products", "", "| Product | Units sold |", "|---|---:|"])
    if metrics.top_products:
        lines.extend(f"| {_escape(name)} | {quantity} |" for name, quantity in metrics.top_products)
    else:
        lines.append("| No product sales recorded | 0 |")
    lines.extend(["", "## Low-stock Alerts", ""])
    if metrics.low_stock_products:
        lines.extend(
            f"- **{_escape(product.title)}** — {product.inventory} unit(s) remaining"
            for product in metrics.low_stock_products
        )
    else:
        lines.append("- No active products are below the configured stock threshold.")
    lines.extend(["", "## AI / Operations Recommendations", ""])
    lines.extend(f"- {_escape(item)}" for item in analysis.recommendations or ("No recommendations available.",))
    lines.extend(["", "## Risks Requiring Review", ""])
    lines.extend(f"- {_escape(item)}" for item in analysis.risks or ("No immediate risks detected by the report rules.",))
    lines.extend(["", "## Report Scope", "", f"- Orders included: {report_date.isoformat()} local day", "- Product inventory: current snapshot", "- Data access: Shopify Admin API read-only queries", ""])
    return "\n".join(lines)

