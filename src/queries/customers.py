import sqlite3
import pandas as pd
from typing import Optional

_TOP_CUSTOMERS_SQL = """
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    o.region,
    SUM(o.revenue)    AS total_revenue,
    COUNT(o.order_id) AS total_orders,
    AVG(o.revenue)    AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
{where}
GROUP BY c.customer_id, c.customer_name, c.city, o.region
ORDER BY total_revenue DESC
LIMIT {limit}
"""

_ACQUISITION_SQL = """
SELECT
    strftime('%Y-%m', c.join_date) AS join_month,
    COUNT(c.customer_id)           AS new_customers
FROM customers c
GROUP BY join_month
ORDER BY join_month
"""

_REPEAT_SQL = """
SELECT
    total_orders,
    COUNT(customer_id) AS customer_count
FROM (
    SELECT customer_id, COUNT(order_id) AS total_orders
    FROM orders
    GROUP BY customer_id
) sub
GROUP BY total_orders
ORDER BY total_orders
"""


def top_customers_by_revenue(
    conn: sqlite3.Connection,
    region: Optional[str] = None,
    limit: int = 10,
) -> pd.DataFrame:
    where = f"WHERE o.region = '{region}'" if region else ""
    sql = _TOP_CUSTOMERS_SQL.format(where=where, limit=limit)
    return pd.read_sql_query(sql, conn)


def customer_acquisition_by_month(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(_ACQUISITION_SQL, conn)


def repeat_purchase_rate(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql_query(_REPEAT_SQL, conn)
    total = df["customer_count"].sum()
    df["pct_of_customers"] = (df["customer_count"] / total * 100).round(1)
    repeat = df[df["total_orders"] > 1]["customer_count"].sum()
    df.attrs["repeat_rate_pct"] = round(repeat / total * 100, 1) if total else 0
    return df
