"""Run full ETL pipeline: CSVs → cleaned DataFrames → SQLite."""
import os
import sqlite3
import sys

BASE = os.path.dirname(__file__)
sys.path.insert(0, BASE)

from src.etl.loader  import load_csv, load_all_regional, REQUIRED_PRODUCT_COLS, REQUIRED_CUSTOMER_COLS
from src.etl.cleaner import clean_orders, clean_products, clean_customers
from src.etl.ingester import Ingester

RAW_DIR = os.path.join(BASE, "data", "raw")
DB_PATH  = os.path.join(BASE, "data", "db", "sales.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def run():
    print("── ETL Pipeline ────────────────────────────────")

    print("[1/5] Loading CSVs…")
    orders_raw    = load_all_regional(RAW_DIR)
    products_raw  = load_csv(os.path.join(RAW_DIR, "products.csv"),  REQUIRED_PRODUCT_COLS)
    customers_raw = load_csv(os.path.join(RAW_DIR, "customers.csv"), REQUIRED_CUSTOMER_COLS)
    print(f"      orders={len(orders_raw):,}  products={len(products_raw)}  customers={len(customers_raw)}")

    print("[2/5] Cleaning…")
    orders    = clean_orders(orders_raw)
    products  = clean_products(products_raw)
    customers = clean_customers(customers_raw)
    print(f"      orders after clean: {len(orders):,}")

    print("[3/5] Connecting to SQLite…")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")

    print("[4/5] Ingesting…")
    ingester = Ingester(conn)
    result = ingester.ingest_all(customers, products, orders)
    conn.close()

    print(f"[5/5] Done — inserted={result.rows_inserted:,}  skipped={result.rows_skipped}  time={result.duration_sec}s")
    print(f"      DB saved to: {DB_PATH}")
    print(f"      DB size: {os.path.getsize(DB_PATH) / 1024:.1f} KB")
    print("────────────────────────────────────────────────")


if __name__ == "__main__":
    run()
