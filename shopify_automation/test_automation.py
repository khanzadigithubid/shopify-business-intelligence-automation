import unittest
from datetime import date
from decimal import Decimal

from .analyzer import calculate_metrics, deterministic_analysis
from .demo_data import build_demo_snapshot
from .report import render_report


class ShopifyAutomationTests(unittest.TestCase):
    def test_metrics_exclude_cancelled_orders(self):
        metrics = calculate_metrics(build_demo_snapshot(), low_stock_threshold=10)
        self.assertEqual(metrics.order_count, 2)
        self.assertEqual(metrics.cancelled_orders, 1)
        self.assertEqual(metrics.gross_sales, Decimal("209.97"))
        self.assertEqual(metrics.top_products[0], ("Premium Hoodie", 2))

    def test_report_contains_aggregate_data_without_customer_fields(self):
        snapshot = build_demo_snapshot()
        metrics = calculate_metrics(snapshot, low_stock_threshold=10)
        report = render_report(date(2026, 8, 9), snapshot, metrics, deterministic_analysis(metrics))
        self.assertIn("Premium Hoodie", report)
        self.assertIn("No customer PII", report)
        self.assertNotIn("customerEmail", report)

    def test_low_stock_alerts(self):
        metrics = calculate_metrics(build_demo_snapshot(), low_stock_threshold=10)
        names = {product.title for product in metrics.low_stock_products}
        self.assertEqual(names, {"Premium Hoodie", "Classic Cap"})


if __name__ == "__main__":
    unittest.main()

