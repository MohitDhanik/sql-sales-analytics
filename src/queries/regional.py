import sqlite3
import pandas as pd
from typing import Optional

_REGIONAL_SUMMARY_SQL = """
SELECT
    o.region,
    SUM(o.revenue)     AS total_revenue,
    COUNT(o.order_id)  AS total_orders,
    AVG(o.revenue)     AS avg_order_value,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM orders o
{where}
GROUP BY o.region
ORDER BY total_revenue DESC
"""

_REGION_PIVOT_SQL = """
SELECT
    o.region,
    strftime('%Y-%m', o.order_date) AS year_month,
    SUM(o.revenue) AS revenue
FROM orders o
GROUP BY o.region, year_month
ORDER BY year_month
"""

_TOP_CITIES_SQL = """
SELECT
    c.city,
    o.region,
    SUM(o.revenue)    AS total_revenue,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
{where}
GROUP BY c.city, o.region
ORDER BY total_revenue DESC
LIMIT {limit}
"""


def regional_summary(conn: sqlite3.Connection, year: Optional[int] = None) -> pd.DataFrame:
    where = f"WHERE strftime('%Y', o.order_date) = '{year}'" if year else ""
    sql = _REGIONAL_SUMMARY_SQL.format(where=where)
    return pd.read_sql_query(sql, conn)


def region_comparison(conn: sqlite3.Connection, metric: str = "revenue") -> pd.DataFrame:
    df = pd.read_sql_query(_REGION_PIVOT_SQL, conn)
    pivot = df.pivot(index="year_month", columns="region", values="revenue").fillna(0)
    pivot.reset_index(inplace=True)
    return pivot


def top_cities_by_revenue(
    conn: sqlite3.Connection,
    region: Optional[str] = None,
    limit: int = 10,
) -> pd.DataFrame:
    where = f"WHERE o.region = '{region}'" if region else ""
    sql = _TOP_CITIES_SQL.format(where=where, limit=limit)
    return pd.read_sql_query(sql, conn)
