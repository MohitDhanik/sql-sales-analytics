import sqlite3
import time
import os
from dataclasses import dataclass
import pandas as pd


@dataclass
class IngestionResult:
    rows_inserted: int
    rows_skipped: int
    duration_sec: float


class Ingester:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _create_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), "..", "db", "schema.sql")
        with open(schema_path) as f:
            self.conn.executescript(f.read())

    def _insert_df(self, df: pd.DataFrame, table: str, pk_col: str) -> tuple[int, int]:
        existing = set(
            row[0] for row in self.conn.execute(f"SELECT {pk_col} FROM {table}").fetchall()
        )
        new_rows = df[~df[pk_col].isin(existing)]
        skipped = len(df) - len(new_rows)
        if len(new_rows) > 0:
            new_rows.to_sql(table, self.conn, if_exists="append", index=False)
        return len(new_rows), skipped

    def ingest_all(
        self,
        customers_df: pd.DataFrame,
        products_df: pd.DataFrame,
        orders_df: pd.DataFrame,
    ) -> IngestionResult:
        t0 = time.time()
        self._create_schema()

        ins, skip = 0, 0
        c_ins, c_skip = self._insert_df(customers_df, "customers", "customer_id")
        p_ins, p_skip = self._insert_df(products_df,  "products",  "product_id")

        # drop generated column and loader-only columns before insert
        orders_insert = orders_df.drop(columns=["revenue", "source_file"], errors="ignore")
        o_ins, o_skip = self._insert_df(orders_insert, "orders", "order_id")

        self.conn.commit()
        return IngestionResult(
            rows_inserted=c_ins + p_ins + o_ins,
            rows_skipped=c_skip + p_skip + o_skip,
            duration_sec=round(time.time() - t0, 3),
        )
