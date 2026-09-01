# SQL Sales Analytics & Reporting Dashboard

Multi-source CSV ingestion → normalised SQLite database → SQL analytics → interactive Streamlit dashboard with KPIs, filters, and charts.

## What it does

Loads raw regional sales data from 4 CSV files, cleans and normalises it into a relational schema, then answers business questions through SQL and visualises them as an interactive dashboard.

```
4 Regional CSVs + Products CSV + Customers CSV
  → ETL (validate · clean · normalise)
  → SQLite (3 tables, FK constraints, indexes)
  → SQL queries (JOINs · GROUP BY · window functions)
  → Streamlit dashboard (KPIs · charts · filters)
```

## Data

| Source | Rows |
|---|---|
| Orders (4 regions) | 1,600 |
| Products | 30 |
| Customers | 200 |
| Date range | Jan 2023 – Dec 2024 |

## SQL features used

- `JOIN` — orders ↔ products ↔ customers
- `GROUP BY` + `SUM / AVG / COUNT` aggregations
- `LAG()` window function — period-over-period growth
- Subqueries — top-N, filtering on aggregates
- Indexes — on `order_date`, `region`, `product_id`
- Generated column — `revenue = quantity * unit_price * (1 - discount_pct)`

## Project structure

```
src/
  etl/      loader.py, cleaner.py, ingester.py
  db/       connection.py, schema.sql
  queries/  revenue.py, regional.py, trends.py, customers.py
  analytics.py
data/raw/   6 source CSVs
tests/      25 pytest tests
app.py      Streamlit dashboard
run_etl.py  standalone ETL script
```

## Setup

```bash
pip install -r requirements.txt

# Build the database
python run_etl.py

# Launch the dashboard
PYTHONPATH=. streamlit run app.py
```

## Run tests

```bash
python -m pytest tests/ -v
```

## Stack

Python · Pandas · SQLite · Streamlit · Matplotlib · Seaborn · pytest
