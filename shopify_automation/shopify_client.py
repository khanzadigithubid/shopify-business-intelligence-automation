"""Minimal read-only Shopify Admin GraphQL client."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
from typing import Any

import requests

from .models import LineItem, Order, Product


class ShopifyAPIError(RuntimeError):
    """Raised when Shopify cannot serve a valid response."""


class ShopifyClient:
    def __init__(self, domain: str, access_token: str, api_version: str, timeout: int = 30):
        self.domain = domain.replace("https://", "").replace("http://", "").strip("/")
        self.endpoint = f"https://{self.domain}/admin/api/{api_version}/graphql.json"
        self.access_token = access_token
        self.timeout = timeout

    def _query(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "Content-Type": "application/json",
                    "X-Shopify-Access-Token": self.access_token,
                    "User-Agent": "shopify-business-automation/1.0",
                },
                json={"query": query, "variables": variables},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ShopifyAPIError(f"Shopify request failed: {exc}") from exc
        except (ValueError, json.JSONDecodeError) as exc:
            raise ShopifyAPIError("Shopify returned invalid JSON") from exc

        errors = payload.get("errors")
        if errors:
            messages = "; ".join(str(item.get("message", "unknown error")) for item in errors)
            raise ShopifyAPIError(f"Shopify GraphQL error: {messages}")
        return payload.get("data", {})

    def get_shop_name(self) -> str:
        data = self._query("query { shop { name } }", {})
        return str(data.get("shop", {}).get("name", self.domain))

    def fetch_orders(self, start: datetime, end: datetime) -> tuple[Order, ...]:
        query = """
        query Orders($first: Int!, $after: String, $query: String!) {
          orders(first: $first, after: $after, query: $query, sortKey: CREATED_AT) {
            pageInfo { hasNextPage endCursor }
            nodes {
              name createdAt displayFinancialStatus displayFulfillmentStatus
              currentTotalPriceSet { shopMoney { amount currencyCode } }
              lineItems(first: 100) {
                nodes { title quantity variant { product { id } } }
              }
            }
          }
        }
        """
        result: list[Order] = []
        after: str | None = None
        search = f"created_at:>={start.isoformat()} created_at:<{end.isoformat()}"
        while True:
            data = self._query(query, {"first": 100, "after": after, "query": search})
            connection = data.get("orders", {})
            for node in connection.get("nodes", []):
                money = node.get("currentTotalPriceSet", {}).get("shopMoney", {})
                try:
                    total = Decimal(str(money.get("amount", "0")))
                except (InvalidOperation, TypeError):
                    total = Decimal("0")
                items = tuple(
                    LineItem(
                        title=str(item.get("title", "Unknown product")),
                        quantity=int(item.get("quantity", 0) or 0),
                        product_id=(item.get("variant") or {}).get("product", {}).get("id"),
                    )
                    for item in node.get("lineItems", {}).get("nodes", [])
                )
                result.append(Order(
                    order_number=str(node.get("name", "Unknown order")),
                    created_at=str(node.get("createdAt", "")),
                    financial_status=str(node.get("displayFinancialStatus", "UNKNOWN")),
                    fulfillment_status=str(node.get("displayFulfillmentStatus", "UNFULFILLED")),
                    total=total,
                    currency=str(money.get("currencyCode", "USD")),
                    line_items=items,
                ))
            page_info = connection.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            after = page_info.get("endCursor")
        return tuple(result)

    def fetch_products(self) -> tuple[Product, ...]:
        query = """
        query Products($first: Int!, $after: String) {
          products(first: $first, after: $after) {
            pageInfo { hasNextPage endCursor }
            nodes { id title status totalInventory }
          }
        }
        """
        result: list[Product] = []
        after: str | None = None
        while True:
            data = self._query(query, {"first": 100, "after": after})
            connection = data.get("products", {})
            result.extend(
                Product(
                    title=str(node.get("title", "Untitled product")),
                    inventory=int(node.get("totalInventory", 0) or 0),
                    status=str(node.get("status", "UNKNOWN")),
                    product_id=node.get("id"),
                )
                for node in connection.get("nodes", [])
            )
            page_info = connection.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            after = page_info.get("endCursor")
        return tuple(result)

