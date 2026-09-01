"""Smoke tests: all Analytics methods return non-empty DataFrames."""
import os
import sys
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.analytics import Analytics

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "db", "sales.db")


@pytest.fixture(scope="module")
def analytics():
    if not os.path.exists(DB_PATH):
        pytest.skip("sales.db not found — run run_etl.py first")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield Analytics(conn)
    conn.close()


def test_top_products_nonempty(analytics):
    df = analytics.top_products()
    assert len(df) > 0


def test_revenue_by_category_nonempty(analytics):
    df = analytics.revenue_by_category()
    assert len(df) > 0


def test_revenue_by_month_nonempty(analytics):
    df = analytics.revenue_by_month()
    assert len(df) > 0


def test_regional_summary_nonempty(analytics):
    df = analytics.regional_summary()
    assert len(df) == 4


def test_pop_growth_nonempty(analytics):
    df = analytics.pop_growth()
    assert len(df) > 0
    assert "growth_pct" in df.columns


def test_quarterly_nonempty(analytics):
    df = analytics.quarterly()
    assert len(df) > 0


def test_top_customers_nonempty(analytics):
    df = analytics.top_customers()
    assert len(df) > 0


def test_kpi_summary_keys(analytics):
    kpi = analytics.kpi_summary()
    for key in ["total_revenue", "total_orders", "avg_order_value", "yoy_growth_pct"]:
        assert key in kpi


def test_kpi_summary_with_filters(analytics):
    kpi = analytics.kpi_summary(region="North", year=2024)
    assert kpi["total_revenue"] > 0
