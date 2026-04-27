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
        "product_id",
        "product_name",
        "order_date",
        "delivered_at",
        "snapshot_date",
        "gmv",
        "commission",
        "effective_commission_rate",
        "returned_flag",
        "return_value",
        "return_shipping_cost",
        "return_reason",
        "return_date",
        "items_count",
        "category",
        "category_id",
        "device",
        "traffic_source",
    ],
    "user_agg_daily": [
        "user_id",
        "date",
        "snapshot_date",
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
        "quarter_returns_count",
        "free_return_eligibility",
        "user_segment_version",
    ],
    "seller_agg_daily": [
        "seller_id",
        "date",
        "snapshot_date",
        "seller_name",
        "gmv_last_30d",
        "return_rate_last_30d",
        "orders_count",
        "avg_order_value",
        "margin_contribution",
        "seller_segment",
        "top_category",
        "effective_commission_rate",
        "commission_tier",
        "seller_segment_version",
    ],
    "product_agg_daily": [
        "product_id",
        "seller_id",
        "date",
        "snapshot_date",
        "product_name",
        "category",
        "category_id",
        "views",
        "orders",
        "return_rate",
        "conversion_rate",
        "avg_price",
        "product_segment",
        "margin_contribution",
        "promotion_score",
    ],
    "category_agg_daily": [
        "category_id",
        "category_name",
        "date",
        "snapshot_date",
        "gmv_last_30d",
        "return_rate_last_30d",
        "margin_contribution",
        "orders_count",
        "contribution_per_order",
        "toxic_share",
    ],
    "interventions_log": [
        "intervention_id",
        "type",
        "target_type",
        "target_id",
        "start_date",
        "end_date",
        "parameters",
        "intervention_code",
        "version",
        "status",
        "eligibility_rule",
        "parameter_json",
    ],
    "scenario_outputs_daily": [
        "date",
        "snapshot_date",
        "intervention_code",
        "scenario_hash",
        "before_window",
        "after_window",
        "observed_delta",
        "delta_margin",
        "delta_gmv",
        "affected_entities",
    ],
}


def _validate_columns(name: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS[name] if column not in dataframe.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {', '.join(missing)}")
    return dataframe


def _normalize_dates(dataframe: pd.DataFrame) -> pd.DataFrame:
    for column in ("date", "snapshot_date", "order_date", "delivered_at", "return_date", "start_date", "end_date"):
        if column in dataframe.columns:
            dataframe[column] = pd.to_datetime(dataframe[column], errors="coerce").dt.date
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
        "category_agg_daily": load_table("category_agg_daily"),
        "interventions_log": load_table("interventions_log"),
        "scenario_outputs_daily": load_table("scenario_outputs_daily"),
    }
