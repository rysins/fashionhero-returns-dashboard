from __future__ import annotations

import math

import pandas as pd

from dashboard.config import (
    SELLER_THRESHOLDS,
    USER_SEGMENT_ORDER,
    USER_THRESHOLDS,
)


def get_available_snapshot_dates(dataframe: pd.DataFrame) -> list:
    return sorted(dataframe["date"].unique())


def select_snapshot(dataframe: pd.DataFrame, snapshot_date) -> pd.DataFrame:
    return dataframe.loc[dataframe["date"] == snapshot_date].copy()


def previous_snapshot(dataframe: pd.DataFrame, snapshot_date) -> pd.DataFrame:
    dates = get_available_snapshot_dates(dataframe)
    earlier = [date for date in dates if date < snapshot_date]
    if not earlier:
        return pd.DataFrame(columns=dataframe.columns)
    return select_snapshot(dataframe, earlier[-1])


def margin_per_order(dataframe: pd.DataFrame, margin_column: str, orders_column: str) -> pd.Series:
    return dataframe[margin_column] / dataframe[orders_column].replace(0, pd.NA)


def assign_user_segment(row: pd.Series) -> str:
    per_order_margin = row["contribution_margin_last_30d"] / max(row["orders_last_30d"], 1)
    if (
        row["return_rate_last_30d"] >= USER_THRESHOLDS.toxic_return_rate
        and per_order_margin <= USER_THRESHOLDS.toxic_margin_per_order
    ):
        return "toxic"
    if (
        row["gmv_last_30d"] >= USER_THRESHOLDS.high_value_gmv
        and row["return_rate_last_30d"] <= USER_THRESHOLDS.high_value_return_rate
        and per_order_margin >= USER_THRESHOLDS.high_value_margin_per_order
    ):
        return "high_value"
    if (
        row["orders_last_30d"] <= USER_THRESHOLDS.tryer_orders_max
        and row["return_rate_last_30d"] >= USER_THRESHOLDS.tryer_return_rate
    ):
        return "tryers"
    return "low_value"


def assign_seller_segment(row: pd.Series) -> str:
    if (
        row["return_rate_last_30d"] >= SELLER_THRESHOLDS.risky_return_rate
        or row["margin_contribution"] < SELLER_THRESHOLDS.risky_margin_contribution
    ):
        return "risky"
    if (
        row["return_rate_last_30d"] >= SELLER_THRESHOLDS.warning_return_rate
        or row["margin_contribution"] < SELLER_THRESHOLDS.warning_margin_contribution
    ):
        return "warning"
    return "healthy"


def enrich_segments(users_df: pd.DataFrame, sellers_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    users = users_df.copy()
    sellers = sellers_df.copy()
    users["calculated_segment"] = users.apply(assign_user_segment, axis=1)
    sellers["calculated_segment"] = sellers.apply(assign_seller_segment, axis=1)
    users["margin_per_order"] = margin_per_order(users, "contribution_margin_last_30d", "orders_last_30d")
    sellers["margin_per_order"] = margin_per_order(sellers, "margin_contribution", "orders_count")
    return users, sellers


def overview_metrics(sellers_df: pd.DataFrame) -> dict[str, float]:
    total_gmv = float(sellers_df["gmv_last_30d"].sum())
    total_margin = float(sellers_df["margin_contribution"].sum())
    total_orders = float(sellers_df["orders_count"].sum())
    weighted_return_rate = float(
        (sellers_df["return_rate_last_30d"] * sellers_df["orders_count"]).sum() / max(total_orders, 1)
    )
    return {
        "gmv": total_gmv,
        "margin": total_margin,
        "orders": total_orders,
        "return_rate": weighted_return_rate,
        "contribution_per_order": total_margin / max(total_orders, 1),
    }


def segment_summary(users_df: pd.DataFrame) -> pd.DataFrame:
    total_users = max(len(users_df), 1)
    total_gmv = max(float(users_df["gmv_last_30d"].sum()), 1.0)
    total_return_cost = max(float(users_df["return_cost_last_30d"].sum()), 1.0)

    grouped = (
        users_df.groupby("segment_label", as_index=False)
        .agg(
            users=("user_id", "count"),
            gmv=("gmv_last_30d", "sum"),
            return_cost=("return_cost_last_30d", "sum"),
            return_rate=("return_rate_last_30d", "mean"),
            margin=("contribution_margin_last_30d", "sum"),
            orders=("orders_last_30d", "sum"),
        )
        .assign(
            users_pct=lambda df: (df["users"] / total_users * 100).round(1),
            gmv_pct=lambda df: (df["gmv"] / total_gmv * 100).round(1),
            return_cost_pct=lambda df: (df["return_cost"] / total_return_cost * 100).round(1),
            margin_per_order=lambda df: (df["margin"] / df["orders"]).round(1),
        )
    )

    grouped["segment_label"] = pd.Categorical(
        grouped["segment_label"], categories=USER_SEGMENT_ORDER, ordered=True
    )
    grouped = grouped.sort_values("segment_label").reset_index(drop=True)

    return grouped[
        [
            "segment_label",
            "users_pct",
            "gmv_pct",
            "return_cost_pct",
            "return_rate",
            "margin",
            "margin_per_order",
        ]
    ]


def toxic_card(users_df: pd.DataFrame) -> dict[str, float]:
    toxic = users_df.loc[users_df["segment_label"] == "toxic"].copy()
    total_users = max(len(users_df), 1)
    total_return_cost = max(float(users_df["return_cost_last_30d"].sum()), 1.0)
    toxic_orders = max(float(toxic["orders_last_30d"].sum()), 1.0)

    return {
        "user_share_pct": round(len(toxic) / total_users * 100, 1),
        "return_cost_share_pct": round(float(toxic["return_cost_last_30d"].sum()) / total_return_cost * 100, 1),
        "margin_per_order": round(float(toxic["contribution_margin_last_30d"].sum()) / toxic_orders, 1),
        "margin_total": round(float(toxic["contribution_margin_last_30d"].sum()), 1),
    }


def migration_summary(previous_df: pd.DataFrame, current_df: pd.DataFrame) -> pd.DataFrame:
    if previous_df.empty:
        return pd.DataFrame(columns=["from_segment", "to_segment", "users"])

    merged = previous_df[["user_id", "segment_label"]].merge(
        current_df[["user_id", "segment_label"]],
        on="user_id",
        suffixes=("_before", "_after"),
    )

    movement = (
        merged.groupby(["segment_label_before", "segment_label_after"], as_index=False)
        .agg(users=("user_id", "count"))
        .rename(columns={"segment_label_before": "from_segment", "segment_label_after": "to_segment"})
        .sort_values(["users", "from_segment", "to_segment"], ascending=[False, True, True])
    )

    return movement


def seller_ranking(sellers_df: pd.DataFrame) -> pd.DataFrame:
    ranked = sellers_df.copy()
    ranked["risk_score"] = (
        ranked["return_rate_last_30d"] * 100
        - ranked["margin_contribution"] / 10
        + ranked["orders_count"] / 5
    )
    ranked = ranked.sort_values(["risk_score", "margin_contribution"], ascending=[False, True]).reset_index(drop=True)
    ranked["impact_rank"] = ranked.index + 1
    return ranked[
        [
            "impact_rank",
            "seller_name",
            "seller_segment",
            "gmv_last_30d",
            "return_rate_last_30d",
            "margin_contribution",
            "avg_order_value",
            "top_category",
        ]
    ]


def simulate_top_returner_intervention(
    users_df: pd.DataFrame,
    top_pct: int,
    return_reduction_pct: int,
    gmv_drop_pct: int,
) -> dict[str, object]:
    targeted_count = max(1, math.ceil(len(users_df) * top_pct / 100))
    targeted = users_df.sort_values(
        ["return_cost_last_30d", "return_rate_last_30d", "gmv_last_30d"],
        ascending=[False, False, False],
    ).head(targeted_count)

    return_savings = float(targeted["return_cost_last_30d"].sum()) * (return_reduction_pct / 100)
    gmv_delta = -float(targeted["gmv_last_30d"].sum()) * (gmv_drop_pct / 100)
    lost_commission = abs(gmv_delta) * 0.22
    margin_delta = return_savings - lost_commission

    return {
        "affected_users": targeted_count,
        "delta_margin": round(margin_delta, 1),
        "delta_gmv": round(gmv_delta, 1),
        "return_cost_saved": round(return_savings, 1),
        "lost_commission": round(lost_commission, 1),
        "targeted_users": targeted[
            ["user_name", "segment_label", "gmv_last_30d", "return_rate_last_30d", "return_cost_last_30d"]
        ].reset_index(drop=True),
    }
