import sqlite3
import pandas as pd
from typing import Optional

_MONTHLY_TREND_SQL = """
SELECT
    strftime('%Y', order_date)    AS year,
    strftime('%m', order_date)    AS month,
    strftime('%Y-%m', order_date) AS year_month,
    SUM(revenue)     AS total_revenue,
    COUNT(order_id)  AS total_orders
FROM orders
{where}
GROUP BY year_month
ORDER BY year_month
"""

_POP_GROWTH_SQL = """
WITH monthly AS (
    SELECT
        CAST(strftime('%Y', order_date) AS INTEGER) AS year,
        CAST(strftime('%m', order_date) AS INTEGER) AS month,
        strftime('%Y-%m', order_date)               AS year_month,
        SUM(revenue) AS revenue
    FROM orders
    GROUP BY year_month
)
SELECT
    year,
    month,
    year_month,
    revenue,
    LAG(revenue) OVER (ORDER BY year, month) AS prev_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY year, month))
        / LAG(revenue) OVER (ORDER BY year, month) * 100,
        2
    ) AS growth_pct
FROM monthly
ORDER BY year, month
"""

_QUARTERLY_SQL = """
SELECT
    strftime('%Y', order_date)  AS year,
    CASE
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 1  AND 3  THEN 'Q1'
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 4  AND 6  THEN 'Q2'
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 7  AND 9  THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    {region_col}
    SUM(revenue)    AS total_revenue,
    COUNT(order_id) AS total_orders
FROM orders
{where}
GROUP BY year, quarter{region_group}
ORDER BY year, quarter
"""

_YOY_CATEGORY_SQL = """
SELECT
    strftime('%Y', o.order_date) AS year,
    p.category,
    SUM(o.revenue) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY year, p.category
ORDER BY year, total_revenue DESC
"""


def monthly_revenue_trend(
    conn: sqlite3.Connection, region: Optional[str] = None
) -> pd.DataFrame:
    where = f"WHERE region = '{region}'" if region else ""
    sql = _MONTHLY_TREND_SQL.format(where=where)
    return pd.read_sql_query(sql, conn)


def period_over_period_growth(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(_POP_GROWTH_SQL, conn)


def quarterly_performance(
    conn: sqlite3.Connection, region: Optional[str] = None
) -> pd.DataFrame:
    where = f"WHERE region = '{region}'" if region else ""
    sql = _QUARTERLY_SQL.format(
        region_col="",
        region_group="",
        where=where,
    )
    return pd.read_sql_query(sql, conn)


def yoy_growth_by_category(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql_query(_YOY_CATEGORY_SQL, conn)
    pivot = df.pivot(index="category", columns="year", values="total_revenue").fillna(0)
    pivot.reset_index(inplace=True)
    years = sorted(df["year"].unique())
    if len(years) >= 2:
        y1, y2 = years[-2], years[-1]
        pivot["yoy_growth_pct"] = ((pivot[y2] - pivot[y1]) / pivot[y1] * 100).round(1)
    return pivot
