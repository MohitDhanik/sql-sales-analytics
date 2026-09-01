"""Generate realistic sample sales data for the SQL Sales Analytics project."""
import pandas as pd
import numpy as np
import os
import random
from datetime import date, timedelta

random.seed(42)
np.random.seed(42)

RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# ── Products ──────────────────────────────────────────────────────────────────
PRODUCTS = [
    # Electronics (highest revenue)
    ("P001", "4K Smart TV 55\"",       "Electronics", 320.0,  649.99),
    ("P002", "Wireless Headphones",    "Electronics", 45.0,   129.99),
    ("P003", "Laptop Pro 15\"",        "Electronics", 550.0, 1199.99),
    ("P004", "Bluetooth Speaker",      "Electronics", 25.0,    79.99),
    ("P005", "Smartphone X12",         "Electronics", 380.0,  899.99),
    ("P006", "Gaming Console",         "Electronics", 280.0,  499.99),
    # Clothing
    ("P007", "Running Jacket",         "Clothing",    22.0,    79.99),
    ("P008", "Denim Jeans",            "Clothing",    18.0,    59.99),
    ("P009", "Wool Sweater",           "Clothing",    20.0,    69.99),
    ("P010", "Athletic Shorts",        "Clothing",    10.0,    34.99),
    ("P011", "Formal Shirt",           "Clothing",    15.0,    49.99),
    ("P012", "Winter Boots",           "Clothing",    45.0,   129.99),
    # Food
    ("P013", "Organic Coffee 1kg",     "Food",         8.0,    24.99),
    ("P014", "Premium Tea Set",        "Food",        12.0,    39.99),
    ("P015", "Protein Bars 30pk",      "Food",        15.0,    44.99),
    ("P016", "Olive Oil 2L",           "Food",         9.0,    29.99),
    ("P017", "Dark Chocolate Box",     "Food",         6.0,    19.99),
    ("P018", "Multivitamin 90ct",      "Food",        10.0,    34.99),
    # Home
    ("P019", "Air Purifier",           "Home",        55.0,   149.99),
    ("P020", "Coffee Maker Deluxe",    "Home",        40.0,   109.99),
    ("P021", "Robot Vacuum",           "Home",       120.0,   299.99),
    ("P022", "Scented Candle Set",     "Home",         8.0,    29.99),
    ("P023", "Bed Sheet Set Queen",    "Home",        25.0,    69.99),
    ("P024", "Smart Thermostat",       "Home",        60.0,   159.99),
    # Sports
    ("P025", "Yoga Mat Premium",       "Sports",      12.0,    39.99),
    ("P026", "Dumbbell Set 20kg",      "Sports",      40.0,    99.99),
    ("P027", "Cycling Helmet",         "Sports",      25.0,    74.99),
    ("P028", "Running Shoes",          "Sports",      45.0,   119.99),
    ("P029", "Tennis Racket Pro",      "Sports",      30.0,    89.99),
    ("P030", "Swim Goggles",           "Sports",       6.0,    24.99),
]
products_df = pd.DataFrame(PRODUCTS, columns=["product_id","product_name","category","cost_price","base_price"])
products_df.to_csv(os.path.join(RAW_DIR, "products.csv"), index=False)
print(f"products.csv — {len(products_df)} rows")

# ── Customers ─────────────────────────────────────────────────────────────────
FIRST = ["James","Sarah","Michael","Emily","David","Jessica","Chris","Ashley","Daniel","Amanda",
         "Matthew","Stephanie","Andrew","Jennifer","Joshua","Lauren","Ryan","Nicole","Justin","Rachel",
         "Kevin","Megan","Brandon","Hannah","Tyler","Brittany","Zachary","Samantha","Nathan","Rebecca",
         "Adam","Christina","Robert","Melissa","Eric","Michelle","Steven","Heather","Timothy","Amy",
         "Aaron","Kimberly","Jacob","Amber","Jeffrey","Elizabeth","Gary","Linda","Frank","Sandra"]
LAST = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore",
        "Taylor","Anderson","Thomas","Jackson","White","Harris","Martin","Thompson","Young","Lee",
        "Walker","Hall","Allen","Sanchez","Wright","King","Scott","Green","Baker","Adams",
        "Nelson","Carter","Mitchell","Perez","Roberts","Turner","Phillips","Campbell","Parker","Evans",
        "Edwards","Collins","Stewart","Flores","Morris","Nguyen","Murphy","Rivera","Cook","Rogers"]
CITIES = {
    "North":  ["Chicago", "Detroit", "Minneapolis", "Milwaukee", "Cleveland", "Indianapolis", "Columbus", "Omaha"],
    "South":  ["Houston", "Dallas", "Atlanta", "Miami", "New Orleans", "Charlotte", "Nashville", "Memphis"],
    "East":   ["New York", "Boston", "Philadelphia", "Baltimore", "Washington DC", "Pittsburgh", "Newark", "Buffalo"],
    "West":   ["Los Angeles", "Seattle", "San Francisco", "Portland", "Denver", "Phoenix", "Las Vegas", "San Diego"],
}
ALL_CITIES = [(c, r) for r, cities in CITIES.items() for c in cities]

customers = []
for i in range(1, 201):
    fn = random.choice(FIRST)
    ln = random.choice(LAST)
    city, region = random.choice(ALL_CITIES)
    join = date(2022, 1, 1) + timedelta(days=random.randint(0, 365))
    customers.append({
        "customer_id": f"C{i:04d}",
        "customer_name": f"{fn} {ln}",
        "email": f"{fn.lower()}.{ln.lower()}{i}@email.com",
        "city": city,
        "join_date": join.isoformat(),
    })
customers_df = pd.DataFrame(customers)
customers_df.to_csv(os.path.join(RAW_DIR, "customers.csv"), index=False)
print(f"customers.csv — {len(customers_df)} rows")

# ── Orders ────────────────────────────────────────────────────────────────────
product_ids = [p[0] for p in PRODUCTS]
product_cat  = {p[0]: p[3] for p in PRODUCTS}   # cost
product_price = {p[0]: p[4] for p in PRODUCTS}

# VIP customers (top 20 = ~20% of volume)
vip_customers = [f"C{i:04d}" for i in random.sample(range(1, 201), 40)]

def make_regional_orders(region, n_orders, order_id_start):
    rows = []
    region_customers = [c["customer_id"] for c in customers
                        if any(c["city"] in CITIES[region] for c in [c])]
    if len(region_customers) < 5:
        region_customers = [c["customer_id"] for c in customers]

    # Category weights vary by region; Electronics always dominant
    cat_weights = {
        "Electronics": 0.38, "Clothing": 0.20, "Food": 0.17, "Home": 0.15, "Sports": 0.10
    }
    cat_products = {}
    for pid, pname, cat, cost, price in PRODUCTS:
        cat_products.setdefault(cat, []).append(pid)

    order_num = order_id_start
    start_date = date(2023, 1, 1)
    end_date   = date(2024, 12, 31)
    total_days = (end_date - start_date).days

    for _ in range(n_orders):
        # 2024 gets 40% more orders than 2023 (growth story)
        if random.random() < 0.42:
            day = random.randint(0, 364)
            year = 2023
        else:
            day = random.randint(0, 365)
            year = 2024
        order_date = date(year, 1, 1) + timedelta(days=day)

        # Q4 spike for North (Oct–Dec +50% more electronics)
        if region == "North" and order_date.month in (10, 11, 12):
            cat = "Electronics" if random.random() < 0.55 else random.choice(list(cat_weights.keys()))
        else:
            cat = random.choices(list(cat_weights.keys()), weights=list(cat_weights.values()))[0]

        pid = random.choice(cat_products[cat])
        base = product_price[pid]

        # VIP customers order more and get bigger discounts
        if random.random() < 0.25:
            cid = random.choice(vip_customers)
            qty = random.randint(2, 8)
            disc = round(random.choice([0.05, 0.10, 0.15, 0.20]), 2)
        else:
            cid = random.choice([c["customer_id"] for c in customers])
            qty = random.randint(1, 3)
            disc = round(random.choice([0.0, 0.0, 0.05, 0.10]), 2)

        # Small price variation ±5%
        unit_price = round(base * random.uniform(0.95, 1.05), 2)

        rows.append({
            "order_id":    f"ORD{order_num:05d}",
            "order_date":  order_date.isoformat(),
            "customer_id": cid,
            "product_id":  pid,
            "quantity":    qty,
            "unit_price":  unit_price,
            "discount_pct": disc,
            "region":      region,
        })
        order_num += 1
    return pd.DataFrame(rows)

region_starts = {"North": 10000, "South": 20000, "East": 30000, "West": 40000}
for region in ["North", "South", "East", "West"]:
    df = make_regional_orders(region, 400, region_starts[region])
    fname = f"sales_{region.lower()}.csv"
    df.to_csv(os.path.join(RAW_DIR, fname), index=False)
    rev = (df["quantity"] * df["unit_price"] * (1 - df["discount_pct"])).sum()
    print(f"{fname} — {len(df)} rows, revenue ${rev:,.0f}")

print("Data generation complete.")
