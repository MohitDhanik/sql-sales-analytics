import os
import sqlite3
import tempfile
import pytest
import pandas as pd
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.etl.loader  import load_csv, load_all_regional
from src.etl.cleaner import clean_orders, clean_products, clean_customers
from src.etl.ingester import Ingester

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def test_loader_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        load_csv("/nonexistent/path/file.csv")


def test_loader_loads_products():
    df = load_csv(os.path.join(RAW_DIR, "products.csv"))
    assert len(df) == 30
    assert "product_id" in df.columns


def test_loader_loads_all_regional():
    df = load_all_regional(RAW_DIR)
    assert len(df) == 1600
    assert "source_file" in df.columns
    assert set(df["region"].unique()) == {"North", "South", "East", "West"}


def test_cleaner_drops_duplicate_order_ids():
    df = pd.DataFrame({
        "order_id":    ["ORD001", "ORD001", "ORD002"],
        "order_date":  ["2023-01-01", "2023-01-01", "2023-01-02"],
        "customer_id": ["C001", "C001", "C002"],
        "product_id":  ["P001", "P001", "P002"],
        "quantity":    [1, 1, 2],
        "unit_price":  [100.0, 100.0, 50.0],
        "discount_pct":[0.0, 0.0, 0.1],
        "region":      ["North", "North", "South"],
    })
    cleaned = clean_orders(df)
    assert len(cleaned) == 2
    assert cleaned["order_id"].is_unique


def test_cleaner_clamps_discount():
    df = pd.DataFrame({
        "order_id":    ["ORD001"],
        "order_date":  ["2023-06-15"],
        "customer_id": ["C001"],
        "product_id":  ["P001"],
        "quantity":    [1],
        "unit_price":  [200.0],
        "discount_pct":[1.5],   # above 1.0 — should be clamped
        "region":      ["North"],
    })
    cleaned = clean_orders(df)
    assert cleaned["discount_pct"].iloc[0] == 1.0


def test_cleaner_clamps_negative_discount():
    df = pd.DataFrame({
        "order_id":    ["ORD001"],
        "order_date":  ["2023-06-15"],
        "customer_id": ["C001"],
        "product_id":  ["P001"],
        "quantity":    [1],
        "unit_price":  [200.0],
        "discount_pct":[-0.5],
        "region":      ["North"],
    })
    cleaned = clean_orders(df)
    assert cleaned["discount_pct"].iloc[0] == 0.0


def test_ingester_inserts_correct_row_count():
    customers_df = pd.DataFrame([
        {"customer_id": "C001", "customer_name": "Alice", "email": "a@b.com", "city": "NY", "join_date": "2023-01-01"},
    ])
    products_df = pd.DataFrame([
        {"product_id": "P001", "product_name": "Widget", "category": "Home", "cost_price": 10.0, "base_price": 25.0},
    ])
    orders_df = pd.DataFrame([
        {"order_id": "ORD001", "order_date": "2023-03-15", "customer_id": "C001",
         "product_id": "P001", "quantity": 2, "unit_price": 25.0, "discount_pct": 0.0, "region": "North"},
        {"order_id": "ORD002", "order_date": "2023-04-10", "customer_id": "C001",
         "product_id": "P001", "quantity": 1, "unit_price": 25.0, "discount_pct": 0.05, "region": "North"},
    ])

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        ingester = Ingester(conn)
        result = ingester.ingest_all(customers_df, products_df, orders_df)
        conn.close()
        # 1 customer + 1 product + 2 orders = 4
        assert result.rows_inserted == 4
        assert result.rows_skipped == 0
    finally:
        os.unlink(db_path)
