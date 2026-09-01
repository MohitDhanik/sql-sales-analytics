import re
import pandas as pd


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df.dropna(subset=["order_date"], inplace=True)
    df["order_date"] = df["order_date"].dt.date.astype(str)

    for col in ["quantity", "unit_price", "discount_pct"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["quantity", "unit_price"], inplace=True)

    # clamp discount_pct to [0, 1]
    df["discount_pct"] = df["discount_pct"].fillna(0.0).clip(0.0, 1.0)
    df["quantity"] = df["quantity"].astype(int)

    # drop exact duplicates then keep first of duplicate order_ids
    df.drop_duplicates(inplace=True)
    df.drop_duplicates(subset=["order_id"], keep="first", inplace=True)

    df["region"] = df["region"].str.strip().str.title()
    return df.reset_index(drop=True)


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["product_name"] = df["product_name"].str.strip()
    df["category"] = df["category"].str.strip().str.title()
    df["cost_price"] = pd.to_numeric(df["cost_price"], errors="coerce")
    df["base_price"] = pd.to_numeric(df["base_price"], errors="coerce")
    df.dropna(subset=["cost_price", "base_price"], inplace=True)
    # enforce cost < base
    mask = df["cost_price"] >= df["base_price"]
    if mask.any():
        df.loc[mask, "cost_price"] = df.loc[mask, "base_price"] * 0.5
    df.drop_duplicates(subset=["product_id"], keep="first", inplace=True)
    return df.reset_index(drop=True)


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["customer_name"] = df["customer_name"].str.strip()
    df["email"] = df["email"].str.strip().str.lower()
    df.loc[~df["email"].apply(lambda e: bool(_EMAIL_RE.match(str(e)))), "email"] = None
    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce").dt.date.astype(str)
    df.drop_duplicates(subset=["customer_id"], keep="first", inplace=True)
    return df.reset_index(drop=True)
