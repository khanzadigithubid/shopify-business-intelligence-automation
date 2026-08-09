"""Explicit local demo data; never used by GitHub Actions."""

from decimal import Decimal

from .models import LineItem, Order, Product, StoreSnapshot


def build_demo_snapshot() -> StoreSnapshot:
    return StoreSnapshot(
        store_name="Demo Shopify Store (Development)",
        orders=(
            Order("#1001", "2026-08-09T09:00:00Z", "PAID", "FULFILLED", Decimal("129.98"), "USD", (LineItem("Premium Hoodie", 2),)),
            Order("#1002", "2026-08-09T11:00:00Z", "PAID", "UNFULFILLED", Decimal("79.99"), "USD", (LineItem("Leather Travel Bag", 1),)),
            Order("#1003", "2026-08-09T12:00:00Z", "CANCELLED", "UNFULFILLED", Decimal("49.99"), "USD", (LineItem("Classic Cap", 1),)),
        ),
        products=(
            Product("Premium Hoodie", 4, "ACTIVE"),
            Product("Leather Travel Bag", 22, "ACTIVE"),
            Product("Classic Cap", 0, "ACTIVE"),
        ),
    )

