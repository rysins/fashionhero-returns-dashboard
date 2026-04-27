from __future__ import annotations

import math

import pandas as pd

from dashboard.config import (
    CATEGORY_THRESHOLDS,
    INTERVENTION_CONFIG,
    SELLER_THRESHOLDS,
    USER_SEGMENT_ORDER,
    USER_THRESHOLDS,
    category_health_badge,
)


def get_available_snapshot_dates(dataframe: pd.DataFrame) -> list:
    return sorted(dataframe["date"].dropna().unique())


def select_snapshot(dataframe: pd.DataFrame, snapshot_date) -> pd.DataFrame:
    return dataframe.loc[dataframe["date"] == snapshot_date].copy()


def previous_snapshot(dataframe: pd.DataFrame, snapshot_date) -> pd.DataFrame:
    dates = get_available_snapshot_dates(dataframe)
    earlier = [date for date in dates if date < snapshot_date]
    if not earlier:
        return pd.DataFrame(columns=dataframe.columns)
    return select_snapshot(dataframe, earlier[-1])


def margin_per_order(dataframe: pd.DataFrame, margin_column: str, orders_column: str) -> pd.Series:
    return (dataframe[margin_column] / dataframe[orders_column].replace(0, pd.NA)).fillna(0)


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


def overview_metrics(
    sellers_df: pd.DataFrame,
    categories_df: pd.DataFrame,
    scenario_outputs_df: pd.DataFrame,
) -> dict[str, float]:
    total_gmv = float(sellers_df["gmv_last_30d"].sum())
    total_margin = float(sellers_df["margin_contribution"].sum())
    total_orders = float(sellers_df["orders_count"].sum())
    weighted_return_rate = float(
        (sellers_df["return_rate_last_30d"] * sellers_df["orders_count"]).sum() / max(total_orders, 1)
    )
    top_risk = categories_df.sort_values(["margin_contribution", "return_rate_last_30d"]).iloc[0]
    projected_margin = scenario_outputs_df["delta_margin"].sum()
    return {
        "gmv": total_gmv,
        "margin": total_margin,
        "orders": total_orders,
        "return_rate": weighted_return_rate,
        "contribution_per_order": total_margin / max(total_orders, 1),
        "highest_risk_category_margin": float(top_risk["margin_contribution"]),
        "highest_risk_category_name": str(top_risk["category_name"]),
        "projected_margin_headroom": float(projected_margin),
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
    grouped["segment_label"] = pd.Categorical(grouped["segment_label"], categories=USER_SEGMENT_ORDER, ordered=True)
    return grouped.sort_values("segment_label").reset_index(drop=True)


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
    return (
        merged.groupby(["segment_label_before", "segment_label_after"], as_index=False)
        .agg(users=("user_id", "count"))
        .rename(columns={"segment_label_before": "from_segment", "segment_label_after": "to_segment"})
        .sort_values(["users", "from_segment", "to_segment"], ascending=[False, True, True])
    )


def seller_ranking(sellers_df: pd.DataFrame) -> pd.DataFrame:
    ranked = sellers_df.copy()
    ranked["risk_score"] = (
        ranked["return_rate_last_30d"] * 100
        - ranked["margin_contribution"] / 10
        + ranked["orders_count"] / 5
    )
    ranked = ranked.sort_values(["risk_score", "margin_contribution"], ascending=[False, True]).reset_index(drop=True)
    ranked["impact_rank"] = ranked.index + 1
    return ranked


def product_ranking(products_df: pd.DataFrame) -> pd.DataFrame:
    ranked = products_df.copy()
    ranked["impact_score"] = ranked["promotion_score"] - ranked["return_rate"] * 60 + ranked["margin_contribution"] / 12
    return ranked.sort_values(["impact_score", "margin_contribution"], ascending=[False, False]).reset_index(drop=True)


def category_overview(categories_df: pd.DataFrame) -> pd.DataFrame:
    categories = categories_df.copy()
    categories["health"] = categories.apply(
        lambda row: category_health_badge(row["return_rate_last_30d"], row["contribution_per_order"]),
        axis=1,
    )
    return categories.sort_values(["health", "margin_contribution", "return_rate_last_30d"], ascending=[True, True, False])


def category_detail(category_id: str, categories_df: pd.DataFrame, products_df: pd.DataFrame, sellers_df: pd.DataFrame) -> dict[str, pd.DataFrame | dict]:
    category_row = categories_df.loc[categories_df["category_id"] == category_id].iloc[0].to_dict()
    products = product_ranking(products_df.loc[products_df["category_id"] == category_id])
    seller_ids = products["seller_id"].unique().tolist()
    sellers = seller_ranking(sellers_df.loc[sellers_df["seller_id"].isin(seller_ids)])
    return {
        "summary": category_row,
        "products": products,
        "sellers": sellers,
    }


def top_destroyers(products_df: pd.DataFrame, sellers_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    product_destroyers = products_df.sort_values(["margin_contribution", "return_rate"], ascending=[True, False]).head(5)
    seller_destroyers = sellers_df.sort_values(["margin_contribution", "return_rate_last_30d"], ascending=[True, False]).head(5)
    return product_destroyers, seller_destroyers


def top_protectors(products_df: pd.DataFrame, sellers_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    product_protectors = products_df.sort_values(["margin_contribution", "promotion_score"], ascending=[False, False]).head(5)
    seller_protectors = sellers_df.sort_values(["margin_contribution", "gmv_last_30d"], ascending=[False, False]).head(5)
    return product_protectors, seller_protectors


def _targeted_count(size: int, pct: int) -> int:
    return max(1, math.ceil(size * pct / 100))


def simulate_soft_penalty(users_df: pd.DataFrame, top_pct: int, return_reduction_pct: int, gmv_drag_pct: int) -> dict[str, object]:
    targeted = users_df.sort_values(
        ["quarter_returns_count", "return_cost_last_30d", "return_rate_last_30d"],
        ascending=[False, False, False],
    ).head(_targeted_count(len(users_df), top_pct))
    return_savings = float(targeted["return_cost_last_30d"].sum()) * (return_reduction_pct / 100)
    gmv_delta = -float(targeted["gmv_last_30d"].sum()) * (gmv_drag_pct / 100)
    lost_commission = abs(gmv_delta) * 0.22
    margin_delta = return_savings - lost_commission
    return {
        "label": INTERVENTION_CONFIG["soft_penalty_high_returners"]["label"],
        "affected_users": int(len(targeted)),
        "delta_margin": round(margin_delta, 1),
        "delta_gmv": round(gmv_delta, 1),
        "return_cost_saved": round(return_savings, 1),
        "lost_commission": round(lost_commission, 1),
        "targeted_entities": targeted[
            ["user_name", "segment_label", "quarter_returns_count", "gmv_last_30d", "return_rate_last_30d", "return_cost_last_30d"]
        ].reset_index(drop=True),
    }


def simulate_dynamic_commission(sellers_df: pd.DataFrame, top_pct: int, uplift_pp: int, gmv_drag_pct: int) -> dict[str, object]:
    targeted = sellers_df.sort_values(
        ["return_rate_last_30d", "gmv_last_30d"], ascending=[False, False]
    ).head(_targeted_count(len(sellers_df), top_pct))
    commission_gain = float(targeted["gmv_last_30d"].sum()) * (uplift_pp / 100)
    gmv_delta = -float(targeted["gmv_last_30d"].sum()) * (gmv_drag_pct / 100)
    seller_retention_cost = abs(gmv_delta) * 0.15
    margin_delta = commission_gain - seller_retention_cost
    return {
        "label": INTERVENTION_CONFIG["dynamic_commission_high_return_sellers"]["label"],
        "affected_sellers": int(len(targeted)),
        "delta_margin": round(margin_delta, 1),
        "delta_gmv": round(gmv_delta, 1),
        "return_cost_saved": round(commission_gain, 1),
        "lost_commission": round(seller_retention_cost, 1),
        "targeted_entities": targeted[
            ["seller_name", "seller_segment", "effective_commission_rate", "gmv_last_30d", "return_rate_last_30d", "margin_contribution"]
        ].reset_index(drop=True),
    }


def simulate_product_promotion(products_df: pd.DataFrame, top_pct: int, gmv_uplift_pct: int, conversion_uplift_pct: int) -> dict[str, object]:
    targeted = product_ranking(products_df).head(_targeted_count(len(products_df), top_pct))
    base_gmv = float((targeted["avg_price"] * targeted["orders"]).sum())
    gmv_delta = base_gmv * (gmv_uplift_pct / 100)
    margin_ratio = float(targeted["margin_contribution"].sum() / max(base_gmv, 1))
    conversion_bonus = float(targeted["margin_contribution"].sum()) * (conversion_uplift_pct / 1000)
    margin_delta = gmv_delta * max(margin_ratio, 0.08) + conversion_bonus
    return {
        "label": INTERVENTION_CONFIG["promote_low_return_products"]["label"],
        "affected_products": int(len(targeted)),
        "delta_margin": round(margin_delta, 1),
        "delta_gmv": round(gmv_delta, 1),
        "return_cost_saved": round(conversion_bonus, 1),
        "lost_commission": 0.0,
        "targeted_entities": targeted[
            ["product_name", "product_segment", "promotion_score", "orders", "return_rate", "margin_contribution"]
        ].reset_index(drop=True),
    }


def scenario_summary(scenarios_df: pd.DataFrame) -> pd.DataFrame:
    return scenarios_df.sort_values(["delta_margin", "delta_gmv"], ascending=[False, False]).reset_index(drop=True)


def category_change(previous_df: pd.DataFrame, current_df: pd.DataFrame) -> pd.DataFrame:
    if previous_df.empty:
        return pd.DataFrame(columns=["category_name", "gmv_delta", "margin_delta", "return_rate_delta"])

    merged = current_df.merge(
        previous_df[["category_id", "gmv_last_30d", "margin_contribution", "return_rate_last_30d"]],
        on="category_id",
        suffixes=("_current", "_previous"),
    )
    merged["gmv_delta"] = merged["gmv_last_30d_current"] - merged["gmv_last_30d_previous"]
    merged["margin_delta"] = merged["margin_contribution_current"] - merged["margin_contribution_previous"]
    merged["return_rate_delta"] = merged["return_rate_last_30d_current"] - merged["return_rate_last_30d_previous"]
    return merged[
        ["category_name", "gmv_delta", "margin_delta", "return_rate_delta"]
    ].sort_values(["margin_delta", "return_rate_delta"], ascending=[True, False])


def category_health_copy(row: dict | pd.Series) -> str:
    return category_health_badge(row["return_rate_last_30d"], row["contribution_per_order"])


def category_threshold_summary() -> dict[str, float]:
    return {
        "healthy_return_rate_max": CATEGORY_THRESHOLDS.healthy_return_rate_max,
        "warning_return_rate_max": CATEGORY_THRESHOLDS.warning_return_rate_max,
        "healthy_margin_per_order_min": CATEGORY_THRESHOLDS.healthy_margin_per_order_min,
        "warning_margin_per_order_min": CATEGORY_THRESHOLDS.warning_margin_per_order_min,
    }
