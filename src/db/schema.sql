CREATE TABLE IF NOT EXISTS customers (
    customer_id   TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email         TEXT,
    city          TEXT,
    join_date     DATE
);

CREATE TABLE IF NOT EXISTS products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    cost_price   REAL NOT NULL,
    base_price   REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id    TEXT PRIMARY KEY,
    order_date  DATE NOT NULL,
    customer_id TEXT NOT NULL,
    product_id  TEXT NOT NULL,
    quantity    INTEGER NOT NULL,
    unit_price  REAL NOT NULL,
    discount_pct REAL DEFAULT 0.0,
    region      TEXT NOT NULL,
    revenue     REAL GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_pct)) STORED,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_date    ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_region  ON orders(region);
CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id);
