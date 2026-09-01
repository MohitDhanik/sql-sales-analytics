import os
import sqlite3
import tempfile
import pytest
import pandas as pd
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.queries.revenue  import top_products_by_revenue, revenue_by_category, revenue_by_month
from src.queries.regional import regional_summary, region_comparison, top_cities_by_revenue
from src.queries.trends   import monthly_revenue_trend, period_over_period_growth, quarterly_performance
from src.queries.customers import top_customers_by_revenue

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "db", "schema.sql")


@pytest.fixture
def test_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = OFF")
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    customers = [
        ("C001", "Alice Smith",  "alice@x.com", "New York",   "2022-06-01"),
        ("C002", "Bob Jones",    "bob@x.com",   "Chicago",    "2022-07-01"),
        ("C003", "Carol White",  "carol@x.com", "Houston",    "2022-08-01"),
        ("C004", "Dan Brown",    "dan@x.com",   "Los Angeles","2022-09-01"),
    ]
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

    products = [
        ("P001", "Laptop",    "Electronics", 400.0,  900.0),
        ("P002", "Headphones","Electronics", 30.0,   80.0),
        ("P003", "T-Shirt",   "Clothing",    10.0,   30.0),
        ("P004", "Coffee",    "Food",        5.0,    15.0),
    ]
    conn.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)

    orders = [
        ("ORD001","2023-01-15","C001","P001",2,900.0,0.0, "North"),
        ("ORD002","2023-02-10","C002","P001",1,900.0,0.1, "South"),
        ("ORD003","2023-03-05","C001","P002",3, 80.0,0.0, "North"),
        ("ORD004","2023-04-20","C003","P003",2, 30.0,0.05,"East"),
        ("ORD005","2023-05-18","C004","P004",5, 15.0,0.0, "West"),
        ("ORD006","2024-01-10","C001","P001",1,900.0,0.0, "North"),
        ("ORD007","2024-02-22","C002","P002",2, 80.0,0.0, "South"),
        ("ORD008","2024-03-14","C003","P001",1,920.0,0.05,"East"),
        ("ORD009","2024-04-01","C004","P003",3, 30.0,0.0, "West"),
        ("ORD010","2024-05-05","C001","P004",2, 15.0,0.0, "North"),
        ("ORD011","2023-06-15","C002","P001",2,900.0,0.0, "South"),
        ("ORD012","2023-07-20","C003","P002",1, 80.0,0.0, "East"),
        ("ORD013","2023-08-08","C004","P003",4, 30.0,0.1, "West"),
        ("ORD014","2023-09-12","C001","P004",3, 15.0,0.0, "North"),
        ("ORD015","2023-10-25","C002","P001",1,880.0,0.0, "South"),
        ("ORD016","2023-11-11","C003","P002",2, 80.0,0.05,"East"),
        ("ORD017","2023-12-01","C004","P003",3, 30.0,0.0, "West"),
        ("ORD018","2024-06-15","C001","P001",2,900.0,0.0, "North"),
        ("ORD019","2024-07-20","C002","P002",1, 80.0,0.0, "South"),
        ("ORD020","2024-08-08","C003","P004",5, 15.0,0.0, "East"),
    ]
    conn.executemany(
        "INSERT INTO orders(order_id,order_date,customer_id,product_id,quantity,unit_price,discount_pct,region) VALUES (?,?,?,?,?,?,?,?)",
        orders
    )
    conn.commit()
    yield conn
    conn.close()


def test_top_products_returns_rows(test_conn):
    df = top_products_by_revenue(test_conn)
    assert len(df) > 0
    assert "total_revenue" in df.columns


def test_top_product_is_laptop(test_conn):
    df = top_products_by_revenue(test_conn, limit=1)
    assert df.iloc[0]["product_name"] == "Laptop"


def test_revenue_by_category_has_electronics(test_conn):
    df = revenue_by_category(test_conn)
    assert "Electronics" in df["category"].values


def test_regional_summary_returns_four_regions(test_conn):
    df = regional_summary(test_conn)
    assert len(df) == 4


def test_regional_summary_has_required_cols(test_conn):
    df = regional_summary(test_conn)
    for col in ["region", "total_revenue", "total_orders", "avg_order_value"]:
        assert col in df.columns


def test_period_over_period_growth_has_growth_col(test_conn):
    df = period_over_period_growth(test_conn)
    assert "growth_pct" in df.columns


def test_monthly_trend_returns_correct_months(test_conn):
    df = monthly_revenue_trend(test_conn)
    # 2023 Jan–Dec + 2024 Jan–Aug = 20 unique months
    assert len(df) >= 12


def test_top_customers_returns_rows(test_conn):
    df = top_customers_by_revenue(test_conn)
    assert len(df) > 0
    assert "customer_name" in df.columns


def test_revenue_by_month_ordered(test_conn):
    df = revenue_by_month(test_conn)
    months = df["year_month"].tolist()
    assert months == sorted(months)
