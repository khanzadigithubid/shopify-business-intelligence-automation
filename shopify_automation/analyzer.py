"""Metrics and optional AI analysis for a privacy-conscious report."""

from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
import json
from typing import Any

import requests

from .models import Analysis, Metrics, StoreSnapshot


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_metrics(snapshot: StoreSnapshot, low_stock_threshold: int) -> Metrics:
    valid_orders = tuple(order for order in snapshot.orders if order.financial_status.upper() != "CANCELLED")
    sales = _money(sum((order.total for order in valid_orders), Decimal("0")))
    average = _money(sales / len(valid_orders)) if valid_orders else Decimal("0.00")
    products = Counter()
    for order in valid_orders:
        for item in order.line_items:
            products[item.title] += item.quantity
    fulfilled = sum(
        1 for order in valid_orders
        if order.fulfillment_status.upper() in {"FULFILLED", "PARTIALLY_FULFILLED"}
    )
    currency = valid_orders[0].currency if valid_orders else "USD"
    return Metrics(
        order_count=len(valid_orders),
        gross_sales=sales,
        average_order_value=average,
        cancelled_orders=len(snapshot.orders) - len(valid_orders),
        fulfilled_orders=fulfilled,
        top_products=tuple(products.most_common(5)),
        low_stock_products=tuple(
            product for product in snapshot.products
            if product.status.upper() == "ACTIVE" and product.inventory <= low_stock_threshold
        ),
        currency=currency,
    )


def deterministic_analysis(metrics: Metrics) -> Analysis:
    highlights = (
        f"{metrics.order_count} non-cancelled order(s) generated {metrics.currency} {metrics.gross_sales} in sales.",
        f"{metrics.fulfilled_orders} order(s) are marked fulfilled.",
    )
    recommendations = []
    if metrics.low_stock_products:
        recommendations.append(
            "Review replenishment for: " + ", ".join(p.title for p in metrics.low_stock_products[:5]) + "."
        )
    if metrics.order_count == 0:
        recommendations.append("Review traffic, checkout errors, and campaign performance because no orders were recorded.")
    else:
        recommendations.append("Prioritize merchandising and retention around the top-selling products listed below.")
    risks = () if not metrics.cancelled_orders else (
        f"{metrics.cancelled_orders} cancelled order(s) require operational review.",
    )
    return Analysis(highlights, tuple(recommendations), risks)


def ai_analysis(metrics: Metrics, api_key: str, base_url: str, model: str, timeout: int = 30) -> Analysis:
    """Ask an OpenAI-compatible API to interpret aggregates only."""
    payload = {
        "metrics": {
            "order_count": metrics.order_count,
            "sales": str(metrics.gross_sales),
            "currency": metrics.currency,
            "average_order_value": str(metrics.average_order_value),
            "cancelled_orders": metrics.cancelled_orders,
            "fulfilled_orders": metrics.fulfilled_orders,
            "top_products": list(metrics.top_products),
            "low_stock_products": [p.title for p in metrics.low_stock_products],
        }
    }
    system = (
        "You are an ecommerce operations analyst. Analyze only the supplied aggregate metrics. "
        "Return strict JSON with arrays: highlights, recommendations, risks. "
        "Do not invent facts, benchmarks, causes, or numbers. Keep each item under 180 characters."
    )
    try:
        response = requests.post(
            base_url.rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(payload)},
                ],
            },
            timeout=timeout,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed: dict[str, Any] = json.loads(content)
        return Analysis(
            tuple(str(x) for x in parsed.get("highlights", [])[:5]),
            tuple(str(x) for x in parsed.get("recommendations", [])[:5]),
            tuple(str(x) for x in parsed.get("risks", [])[:5]),
            source=f"ai:{model}",
        )
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
        return deterministic_analysis(metrics)

