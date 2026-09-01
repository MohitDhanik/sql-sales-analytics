import sqlite3
import pandas as pd
from typing import Optional

_TOP_PRODUCTS_SQL = """
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.revenue)   AS total_revenue,
    COUNT(o.order_id) AS total_orders,
    AVG(o.unit_price) AS avg_price
FROM orders o
JOIN products p ON o.product_id = p.product_id
{where}
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT {limit}
"""

_REVENUE_BY_CATEGORY_SQL = """
SELECT
    p.category,
    SUM(o.revenue)    AS total_revenue,
    COUNT(o.order_id) AS total_orders,
    AVG(o.unit_price) AS avg_price
FROM orders o
JOIN products p ON o.product_id = p.product_id
{where}
GROUP BY p.category
ORDER BY total_revenue DESC
"""

_REVENUE_BY_MONTH_SQL = """
SELECT
    strftime('%Y', o.order_date) AS year,
    strftime('%m', o.order_date) AS month,
    strftime('%Y-%m', o.order_date) AS year_month,
    SUM(o.revenue)    AS total_revenue,
    COUNT(o.order_id) AS total_orders
FROM orders o
{where}
GROUP BY year_month
ORDER BY year_month
"""


def _build_where(region: Optional[str] = None, year: Optional[int] = None) -> str:
    clauses = []
    if region:
        clauses.append(f"o.region = '{region}'")
    if year:
        clauses.append(f"strftime('%Y', o.order_date) = '{year}'")
    return ("WHERE " + " AND ".join(clauses)) if clauses else ""


def top_products_by_revenue(
    conn: sqlite3.Connection,
    region: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 10,
) -> pd.DataFrame:
    sql = _TOP_PRODUCTS_SQL.format(where=_build_where(region, year), limit=limit)
    return pd.read_sql_query(sql, conn)


def revenue_by_category(
    conn: sqlite3.Connection,
    region: Optional[str] = None,
    year: Optional[int] = None,
) -> pd.DataFrame:
    sql = _REVENUE_BY_CATEGORY_SQL.format(where=_build_where(region, year))
    df = pd.read_sql_query(sql, conn)
    total = df["total_revenue"].sum()
    df["market_share_pct"] = (df["total_revenue"] / total * 100).round(1) if total else 0
    return df


def revenue_by_month(
    conn: sqlite3.Connection,
    region: Optional[str] = None,
) -> pd.DataFrame:
    sql = _REVENUE_BY_MONTH_SQL.format(where=_build_where(region))
    return pd.read_sql_query(sql, conn)
