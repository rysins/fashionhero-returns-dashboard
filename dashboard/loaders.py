from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

from dashboard.build_database import DB_PATH, build_database_if_missing

BASE_DIR = Path(__file__).resolve().parent

REQUIRED_COLUMNS = {
    "orders_fact": [
        "order_id",
        "user_id",
        "seller_id",
        "order_date",
        "gmv",
        "commission",
        "returned_flag",
        "return_value",
        "return_reason",
        "return_date",
        "items_count",
        "category",
        "device",
        "traffic_source",
    ],
    "user_agg_daily": [
        "user_id",
        "date",
        "user_name",
        "orders_last_30d",
        "gmv_last_30d",
        "return_rate_last_30d",
        "return_cost_last_30d",
        "avg_items_per_order",
        "lifetime_orders",
        "lifetime_return_rate",
        "contribution_margin_last_30d",
        "segment_label",
        "primary_device",
    ],
    "seller_agg_daily": [
        "seller_id",
        "date",
        "seller_name",
        "gmv_last_30d",
        "return_rate_last_30d",
        "orders_count",
        "avg_order_value",
        "margin_contribution",
        "seller_segment",
        "top_category",
    ],
    "product_agg_daily": [
        "product_id",
        "seller_id",
        "date",
        "product_name",
        "category",
        "views",
        "orders",
        "return_rate",
        "conversion_rate",
        "avg_price",
        "product_segment",
    ],
    "interventions_log": [
        "intervention_id",
        "type",
        "target_type",
        "target_id",
        "start_date",
        "end_date",
        "parameters",
    ],
}


def _validate_columns(name: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS[name] if column not in dataframe.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {', '.join(missing)}")
    return dataframe


def _normalize_dates(dataframe: pd.DataFrame) -> pd.DataFrame:
    if "date" in dataframe.columns:
        dataframe["date"] = pd.to_datetime(dataframe["date"]).dt.date
    if "order_date" in dataframe.columns:
        dataframe["order_date"] = pd.to_datetime(dataframe["order_date"]).dt.date
    if "return_date" in dataframe.columns:
        dataframe["return_date"] = pd.to_datetime(dataframe["return_date"], errors="coerce").dt.date
    if "start_date" in dataframe.columns:
        dataframe["start_date"] = pd.to_datetime(dataframe["start_date"]).dt.date
    if "end_date" in dataframe.columns:
        dataframe["end_date"] = pd.to_datetime(dataframe["end_date"], errors="coerce").dt.date
    return dataframe


@st.cache_data(show_spinner=False)
def load_table(name: str) -> pd.DataFrame:
    build_database_if_missing()
    with sqlite3.connect(DB_PATH) as connection:
        dataframe = pd.read_sql_query(f"select * from {name}", connection)
    dataframe = _validate_columns(name, dataframe)
    return _normalize_dates(dataframe)


def load_all_data() -> dict[str, pd.DataFrame]:
    return {
        "orders_fact": load_table("orders_fact"),
        "user_agg_daily": load_table("user_agg_daily"),
        "seller_agg_daily": load_table("seller_agg_daily"),
        "product_agg_daily": load_table("product_agg_daily"),
        "interventions_log": load_table("interventions_log"),
    }
