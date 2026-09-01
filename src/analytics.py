"""High-level analytics API — thin wrapper over individual query modules."""
import sqlite3
from typing import Optional
import pandas as pd

from src.queries import revenue, regional, trends, customers


class Analytics:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # Revenue
    def top_products(self, region=None, year=None, limit=10) -> pd.DataFrame:
        return revenue.top_products_by_revenue(self.conn, region, year, limit)

    def revenue_by_category(self, region=None, year=None) -> pd.DataFrame:
        return revenue.revenue_by_category(self.conn, region, year)

    def revenue_by_month(self, region=None) -> pd.DataFrame:
        return revenue.revenue_by_month(self.conn, region)

    # Regional
    def regional_summary(self, year=None) -> pd.DataFrame:
        return regional.regional_summary(self.conn, year)

    def region_comparison(self) -> pd.DataFrame:
        return regional.region_comparison(self.conn)

    def top_cities(self, region=None, limit=10) -> pd.DataFrame:
        return regional.top_cities_by_revenue(self.conn, region, limit)

    # Trends
    def monthly_trend(self, region=None) -> pd.DataFrame:
        return trends.monthly_revenue_trend(self.conn, region)

    def pop_growth(self) -> pd.DataFrame:
        return trends.period_over_period_growth(self.conn)

    def quarterly(self, region=None) -> pd.DataFrame:
        return trends.quarterly_performance(self.conn, region)

    def yoy_by_category(self) -> pd.DataFrame:
        return trends.yoy_growth_by_category(self.conn)

    # Customers
    def top_customers(self, region=None, limit=10) -> pd.DataFrame:
        return customers.top_customers_by_revenue(self.conn, region, limit)

    def acquisition(self) -> pd.DataFrame:
        return customers.customer_acquisition_by_month(self.conn)

    def repeat_rate(self) -> pd.DataFrame:
        return customers.repeat_purchase_rate(self.conn)

    # KPI summary
    def kpi_summary(self, region: Optional[str] = None, year: Optional[int] = None) -> dict:
        clauses = []
        if region:
            clauses.append(f"region = '{region}'")
        if year:
            clauses.append(f"strftime('%Y', order_date) = '{year}'")
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        row = self.conn.execute(f"""
            SELECT
                COALESCE(SUM(revenue), 0)    AS total_revenue,
                COUNT(order_id)              AS total_orders,
                COALESCE(AVG(revenue), 0)    AS avg_order_value,
                COUNT(DISTINCT customer_id)  AS unique_customers
            FROM orders {where}
        """).fetchone()

        # YoY growth
        years = [r[0] for r in self.conn.execute("SELECT DISTINCT strftime('%Y', order_date) FROM orders ORDER BY 1").fetchall()]
        yoy = None
        if len(years) >= 2:
            y_prev, y_curr = years[-2], years[-1]
            rev_prev = self.conn.execute(
                f"SELECT SUM(revenue) FROM orders WHERE strftime('%Y', order_date) = '{y_prev}'" +
                (f" AND region = '{region}'" if region else "")
            ).fetchone()[0] or 0
            rev_curr = self.conn.execute(
                f"SELECT SUM(revenue) FROM orders WHERE strftime('%Y', order_date) = '{y_curr}'" +
                (f" AND region = '{region}'" if region else "")
            ).fetchone()[0] or 0
            yoy = round((rev_curr - rev_prev) / rev_prev * 100, 1) if rev_prev else None

        return {
            "total_revenue": row[0],
            "total_orders": row[1],
            "avg_order_value": row[2],
            "unique_customers": row[3],
            "yoy_growth_pct": yoy,
        }
