"""Small typed data models used by the Shopify reporting workflow."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LineItem:
    title: str
    quantity: int
    product_id: str | None = None


@dataclass(frozen=True)
class Order:
    order_number: str
    created_at: str
    financial_status: str
    fulfillment_status: str
    total: Decimal
    currency: str
    line_items: tuple[LineItem, ...] = ()


@dataclass(frozen=True)
class Product:
    title: str
    inventory: int
    status: str
    product_id: str | None = None


@dataclass(frozen=True)
class StoreSnapshot:
    store_name: str
    orders: tuple[Order, ...] = ()
    products: tuple[Product, ...] = ()


@dataclass(frozen=True)
class Metrics:
    order_count: int
    gross_sales: Decimal
    average_order_value: Decimal
    cancelled_orders: int
    fulfilled_orders: int
    top_products: tuple[tuple[str, int], ...]
    low_stock_products: tuple[Product, ...]
    currency: str


@dataclass(frozen=True)
class Analysis:
    highlights: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    source: str = "deterministic"

