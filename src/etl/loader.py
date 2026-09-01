import os
import pandas as pd
from typing import Optional

REQUIRED_ORDER_COLS = {"order_id", "order_date", "customer_id", "product_id",
                       "quantity", "unit_price", "discount_pct", "region"}
REQUIRED_PRODUCT_COLS = {"product_id", "product_name", "category", "cost_price", "base_price"}
REQUIRED_CUSTOMER_COLS = {"customer_id", "customer_name", "email", "city", "join_date"}


def load_csv(path: str, required_cols: Optional[set] = None) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path)
    if required_cols:
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns in {path}: {missing}")
    return df


def load_all_regional(data_dir: str) -> pd.DataFrame:
    regions = ["north", "south", "east", "west"]
    frames = []
    for region in regions:
        path = os.path.join(data_dir, f"sales_{region}.csv")
        df = load_csv(path, REQUIRED_ORDER_COLS)
        df["source_file"] = f"sales_{region}.csv"
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
