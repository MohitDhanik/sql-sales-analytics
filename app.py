"""SQL Sales Analytics Dashboard — dark finance aesthetic."""
import os
import sys
import sqlite3

import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from src.analytics import Analytics
from run_etl import run as run_etl

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #111827 0%, #1a2236 100%);
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #f59e0b;
    line-height: 1;
}
.kpi-sub {
    font-size: 0.78rem;
    color: #9ca3af;
    margin-top: 6px;
}
.kpi-up   { color: #10b981; }
.kpi-down { color: #ef4444; }

/* Section headers */
.section-header {
    font-size: 0.70rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #f59e0b;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 6px;
    margin: 24px 0 16px;
}

/* Table styling */
.dataframe { font-size: 0.82rem !important; }
.stDataFrame thead tr th { background-color: #111827 !important; color: #f59e0b !important; }

/* Tabs */
.stTabs [role="tab"]           { color: #9ca3af; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.06em; }
.stTabs [role="tab"][aria-selected="true"] { color: #f59e0b; border-bottom: 2px solid #f59e0b; }

/* Sidebar */
section[data-testid="stSidebar"] { background-color: #0d1220 !important; }
</style>
""", unsafe_allow_html=True)

# ── Chart theme ───────────────────────────────────────────────────────────────
BG      = "#0a0e1a"
BG2     = "#111827"
AMBER   = "#f59e0b"
AMBER2  = "#fbbf24"
GRID    = "#1e293b"
TEXT    = "#e2e8f0"
GREEN   = "#10b981"
RED     = "#ef4444"
BLUES   = ["#f59e0b","#fbbf24","#d97706","#b45309","#92400e"]
CAT_COLORS = ["#f59e0b","#3b82f6","#10b981","#8b5cf6","#ef4444"]

matplotlib.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    BG2,
    "axes.edgecolor":    GRID,
    "axes.labelcolor":   TEXT,
    "xtick.color":       "#6b7280",
    "ytick.color":       "#6b7280",
    "text.color":        TEXT,
    "grid.color":        GRID,
    "grid.linewidth":    0.6,
    "font.family":       "sans-serif",
    "font.size":         9,
})


def fmt_currency(val):
    if val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    if val >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:.0f}"


def dark_fig(w=8, h=4):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG)
    ax.set_facecolor(BG2)
    ax.spines[:].set_color(GRID)
    return fig, ax


# ── DB connection ─────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "db", "sales.db")


@st.cache_resource
def get_analytics():
    if not os.path.exists(DB_PATH):
        run_etl()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return Analytics(conn)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 20px'>
        <div style='font-size:1.3rem; font-weight:700; color:#f59e0b; letter-spacing:0.08em'>
            ◈ SALES ANALYTICS
        </div>
        <div style='font-size:0.68rem; color:#4b5563; letter-spacing:0.14em; margin-top:4px'>
            MULTI-REGION DASHBOARD
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    region_opts = ["All Regions", "North", "South", "East", "West"]
    region_sel  = st.selectbox("Region", region_opts)
    region      = None if region_sel == "All Regions" else region_sel

    year_opts = ["All Years", "2023", "2024"]
    year_sel  = st.selectbox("Year", year_opts)
    year      = None if year_sel == "All Years" else int(year_sel)

    st.markdown("---")
    if st.button("⟳  Rebuild Database", use_container_width=True):
        with st.spinner("Running ETL…"):
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            get_analytics.clear()
            run_etl()
            st.success("Database rebuilt.")
            st.rerun()

    st.markdown("""
    <div style='position:absolute; bottom:16px; left:0; right:0; text-align:center;
                font-size:0.62rem; color:#374151; letter-spacing:0.1em'>
        SQL SALES ANALYTICS v1.0
    </div>
    """, unsafe_allow_html=True)

# ── Load analytics ────────────────────────────────────────────────────────────
analytics = get_analytics()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["  OVERVIEW  ", "  PRODUCTS  ", "  REGIONS  ", "  TRENDS  "])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    kpi = analytics.kpi_summary(region=region, year=year)
    rev, orders, aov, yoy = (
        kpi["total_revenue"], kpi["total_orders"],
        kpi["avg_order_value"], kpi["yoy_growth_pct"],
    )
    yoy_html = (
        f'<div class="kpi-sub kpi-up">▲ {yoy:.1f}% YoY</div>' if yoy and yoy > 0
        else f'<div class="kpi-sub kpi-down">▼ {abs(yoy):.1f}% YoY</div>' if yoy
        else '<div class="kpi-sub">—</div>'
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "TOTAL REVENUE",     fmt_currency(rev),     yoy_html),
        (c2, "TOTAL ORDERS",      f"{orders:,}",          '<div class="kpi-sub">transactions</div>'),
        (c3, "AVG ORDER VALUE",   fmt_currency(aov),      '<div class="kpi-sub">per order</div>'),
        (c4, "UNIQUE CUSTOMERS",  f"{kpi['unique_customers']:,}", '<div class="kpi-sub">active buyers</div>'),
    ]:
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val}</div>{sub}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-header">REVENUE TREND</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        trend = analytics.revenue_by_month(region=region)
        fig, ax = dark_fig(9, 3.6)
        x = range(len(trend))
        ax.plot(x, trend["total_revenue"], color=AMBER, linewidth=2, zorder=3)
        ax.fill_between(x, trend["total_revenue"], alpha=0.12, color=AMBER)
        ax.set_xticks(list(x)[::3])
        ax.set_xticklabels(trend["year_month"].iloc[::3], rotation=35, ha="right", fontsize=7.5)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_currency(v)))
        ax.set_title("Monthly Revenue", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col_right:
        cat_df = analytics.revenue_by_category(region=region, year=year)
        fig, ax = dark_fig(5, 3.6)
        bars = ax.barh(cat_df["category"][::-1], cat_df["total_revenue"][::-1],
                       color=CAT_COLORS[:len(cat_df)], edgecolor="none", height=0.55)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_currency(v)))
        for bar, val in zip(bars, cat_df["total_revenue"][::-1]):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                    fmt_currency(val), va="center", fontsize=7.5, color=TEXT)
        ax.set_title("Revenue by Category", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
        ax.grid(axis="x", linestyle="--", alpha=0.4)
        ax.set_xlim(0, cat_df["total_revenue"].max() * 1.18)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.markdown('<div class="section-header">REGIONAL PERFORMANCE</div>', unsafe_allow_html=True)
    reg_df = analytics.regional_summary(year=year)
    fig, ax = dark_fig(10, 2.8)
    palette = [AMBER if r == region else "#334155" for r in reg_df["region"]]
    bars = ax.bar(reg_df["region"], reg_df["total_revenue"], color=palette, width=0.5, edgecolor="none")
    for bar, val in zip(bars, reg_df["total_revenue"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
                fmt_currency(val), ha="center", va="bottom", fontsize=8.5, color=TEXT, fontweight="500")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_currency(v)))
    ax.set_title("Regional Revenue Comparison", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    prod_df = analytics.top_products(region=region, year=year, limit=10)
    cat_df  = analytics.revenue_by_category(region=region, year=year)

    st.markdown('<div class="section-header">TOP 10 PRODUCTS BY REVENUE</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        fig, ax = dark_fig(9, 4.2)
        colors = [AMBER if i == 0 else "#334155" for i in range(len(prod_df))]
        bars = ax.barh(prod_df["product_name"][::-1], prod_df["total_revenue"][::-1],
                       color=colors[::-1], edgecolor="none", height=0.6)
        for bar, val in zip(bars, prod_df["total_revenue"][::-1]):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                    fmt_currency(val), va="center", fontsize=7.5, color=TEXT)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_currency(v)))
        ax.set_title("Top Products by Revenue", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
        ax.grid(axis="x", linestyle="--", alpha=0.35)
        ax.set_xlim(0, prod_df["total_revenue"].max() * 1.18)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col_r:
        fig, ax = dark_fig(5, 4.2)
        wedges, texts, autotexts = ax.pie(
            cat_df["total_revenue"],
            labels=cat_df["category"],
            colors=CAT_COLORS[:len(cat_df)],
            autopct="%1.1f%%",
            pctdistance=0.75,
            wedgeprops={"edgecolor": BG, "linewidth": 2, "width": 0.55},
            startangle=90,
        )
        for t in texts:
            t.set_color(TEXT); t.set_fontsize(8)
        for t in autotexts:
            t.set_color(BG2); t.set_fontsize(7.5); t.set_fontweight("bold")
        ax.set_facecolor(BG)
        ax.set_title("Revenue by Category", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.markdown('<div class="section-header">CATEGORY PERFORMANCE TABLE</div>', unsafe_allow_html=True)
    display_cat = cat_df.copy()
    display_cat["total_revenue"] = display_cat["total_revenue"].apply(fmt_currency)
    display_cat["avg_price"] = display_cat["avg_price"].apply(lambda v: f"${v:.2f}")
    display_cat["market_share_pct"] = display_cat["market_share_pct"].apply(lambda v: f"{v:.1f}%")
    display_cat.columns = ["Category","Revenue","Orders","Avg Price","Market Share"]
    st.dataframe(display_cat, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">TOP 10 PRODUCTS TABLE</div>', unsafe_allow_html=True)
    prod_tbl = prod_df[["product_name","category","total_revenue","total_orders","avg_price"]].copy()
    prod_tbl["total_revenue"] = prod_tbl["total_revenue"].apply(fmt_currency)
    prod_tbl["avg_price"] = prod_tbl["avg_price"].apply(lambda v: f"${v:.2f}")
    prod_tbl.columns = ["Product","Category","Revenue","Orders","Avg Price"]
    st.dataframe(prod_tbl, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — REGIONS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    reg_summary = analytics.regional_summary()

    st.markdown('<div class="section-header">REGIONAL SCORECARDS</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, row in reg_summary.iterrows():
        with cols[i % 4]:
            highlighted = row["region"] == region
            border_color = AMBER if highlighted else "#1e3a5f"
            st.markdown(f"""
            <div style='background:#111827; border:1px solid {border_color}; border-radius:8px;
                        padding:16px; margin-bottom:8px;'>
                <div style='font-size:0.7rem; font-weight:700; letter-spacing:0.12em;
                            text-transform:uppercase; color:#f59e0b; margin-bottom:10px'>
                    {row["region"]}
                </div>
                <div style='font-size:1.4rem; font-weight:700; color:#e2e8f0'>
                    {fmt_currency(row["total_revenue"])}
                </div>
                <div style='font-size:0.72rem; color:#6b7280; margin-top:6px'>
                    {int(row["total_orders"]):,} orders
                    &nbsp;·&nbsp; AOV {fmt_currency(row["avg_order_value"])}
                </div>
                <div style='font-size:0.72rem; color:#6b7280'>
                    {int(row["unique_customers"])} unique customers
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">MONTHLY REVENUE HEATMAP BY REGION</div>', unsafe_allow_html=True)
    pivot = analytics.region_comparison()
    if "year_month" in pivot.columns:
        pivot = pivot.set_index("year_month")
    # Take last 24 months for readability
    pivot = pivot.tail(24)

    fig, ax = dark_fig(12, 4)
    sns.heatmap(
        pivot.T,
        ax=ax,
        cmap=sns.color_palette("YlOrBr", as_cmap=True),
        linewidths=0.3,
        linecolor=BG,
        annot=True,
        fmt=".0f",
        annot_kws={"size": 6.5, "color": BG2},
        cbar_kws={"shrink": 0.7},
    )
    ax.set_title("Monthly Revenue Heatmap (Region × Month)", color=AMBER2, fontsize=10, fontweight="bold", pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    ax.tick_params(axis="y", rotation=0,  labelsize=8)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown('<div class="section-header">TOP CITIES BY REVENUE</div>', unsafe_allow_html=True)
    cities_df = analytics.top_cities(region=region, limit=12)
    fig, ax = dark_fig(10, 3.5)
    colors = [AMBER if i < 3 else "#334155" for i in range(len(cities_df))]
    bars = ax.barh(cities_df["city"][::-1], cities_df["total_revenue"][::-1],
                   color=colors[::-1], edgecolor="none", height=0.55)
    for bar, val in zip(bars, cities_df["total_revenue"][::-1]):
        ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                fmt_currency(val), va="center", fontsize=7.5, color=TEXT)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_currency(v)))
    ax.set_title("Top Cities by Revenue", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
    ax.set_xlim(0, cities_df["total_revenue"].max() * 1.18)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">2023 vs 2024 MONTHLY REVENUE</div>', unsafe_allow_html=True)

    trend_all = analytics.monthly_trend(region=region)
    t2023 = trend_all[trend_all["year"] == "2023"].reset_index(drop=True)
    t2024 = trend_all[trend_all["year"] == "2024"].reset_index(drop=True)

    fig, ax = dark_fig(12, 3.8)
    months = list(range(1, 13))
    rev23 = [t2023[t2023["month"] == f"{m:02d}"]["total_revenue"].sum() for m in months]
    rev24 = [t2024[t2024["month"] == f"{m:02d}"]["total_revenue"].sum() for m in months]
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    ax.plot(months, rev23, color="#3b82f6", linewidth=2, marker="o", markersize=4, label="2023")
    ax.plot(months, rev24, color=AMBER,    linewidth=2, marker="o", markersize=4, label="2024")
    ax.fill_between(months, rev23, alpha=0.07, color="#3b82f6")
    ax.fill_between(months, rev24, alpha=0.07, color=AMBER)
    ax.set_xticks(months)
    ax.set_xticklabels(month_labels, fontsize=8.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_currency(v)))
    ax.legend(frameon=False, labelcolor=TEXT, fontsize=9)
    ax.set_title("2023 vs 2024 Monthly Revenue", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
    ax.grid(linestyle="--", alpha=0.35)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">MONTH-OVER-MONTH GROWTH %</div>', unsafe_allow_html=True)
        pop = analytics.pop_growth()
        pop_valid = pop.dropna(subset=["growth_pct"]).tail(18)
        fig, ax = dark_fig(7, 3.5)
        colors = [GREEN if g >= 0 else RED for g in pop_valid["growth_pct"]]
        ax.bar(range(len(pop_valid)), pop_valid["growth_pct"], color=colors, width=0.7, edgecolor="none")
        ax.axhline(0, color=GRID, linewidth=1)
        ax.set_xticks(range(len(pop_valid)))
        ax.set_xticklabels(pop_valid["year_month"], rotation=45, ha="right", fontsize=6.5)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax.set_title("Month-over-Month Growth %", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col_r:
        st.markdown('<div class="section-header">QUARTERLY PERFORMANCE</div>', unsafe_allow_html=True)
        qtr = analytics.quarterly(region=region)
        fig, ax = dark_fig(7, 3.5)
        y2023 = qtr[qtr["year"] == "2023"]
        y2024 = qtr[qtr["year"] == "2024"]
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        x = np.arange(4)
        w = 0.35
        rev23q = [y2023[y2023["quarter"] == q]["total_revenue"].sum() for q in quarters]
        rev24q = [y2024[y2024["quarter"] == q]["total_revenue"].sum() for q in quarters]
        ax.bar(x - w/2, rev23q, width=w, color="#3b82f6", label="2023", edgecolor="none")
        ax.bar(x + w/2, rev24q, width=w, color=AMBER,    label="2024", edgecolor="none")
        ax.set_xticks(x)
        ax.set_xticklabels(quarters, fontsize=9)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_currency(v)))
        ax.legend(frameon=False, labelcolor=TEXT, fontsize=8.5)
        ax.set_title("Quarterly Performance", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.markdown('<div class="section-header">YOY GROWTH BY CATEGORY</div>', unsafe_allow_html=True)
    yoy_cat = analytics.yoy_by_category()
    if "yoy_growth_pct" in yoy_cat.columns:
        fig, ax = dark_fig(10, 2.8)
        colors = [GREEN if g >= 0 else RED for g in yoy_cat["yoy_growth_pct"]]
        bars = ax.bar(yoy_cat["category"], yoy_cat["yoy_growth_pct"], color=colors, width=0.5, edgecolor="none")
        for bar, val in zip(bars, yoy_cat["yoy_growth_pct"]):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + (0.3 if val >= 0 else -1.5),
                    f"{val:.1f}%", ha="center", va="bottom", fontsize=8.5, color=TEXT)
        ax.axhline(0, color=GRID, linewidth=1)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax.set_title("YoY Revenue Growth by Category (2023 → 2024)", color=AMBER2, fontsize=10, fontweight="bold", pad=10)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    # SQL Explorer
    st.markdown('<div class="section-header">SQL QUERY EXPLORER</div>', unsafe_allow_html=True)
    with st.expander("View SQL queries used in this dashboard"):
        st.code("""-- Period-over-period growth (window function)
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
    year, month, year_month, revenue,
    LAG(revenue) OVER (ORDER BY year, month) AS prev_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY year, month))
        / LAG(revenue) OVER (ORDER BY year, month) * 100, 2
    ) AS growth_pct
FROM monthly
ORDER BY year, month;

-- Top products by revenue (JOIN + GROUP BY)
SELECT
    p.product_id, p.product_name, p.category,
    SUM(o.revenue)    AS total_revenue,
    COUNT(o.order_id) AS total_orders,
    AVG(o.unit_price) AS avg_price
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- Regional summary
SELECT
    o.region,
    SUM(o.revenue)     AS total_revenue,
    COUNT(o.order_id)  AS total_orders,
    AVG(o.revenue)     AS avg_order_value,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM orders o
GROUP BY o.region
ORDER BY total_revenue DESC;""", language="sql")
