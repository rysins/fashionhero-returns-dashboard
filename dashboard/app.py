from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.config import CATEGORY_HEALTH_COLORS, SELLER_SEGMENT_COLORS, USER_SEGMENT_COLORS
from dashboard.loaders import load_all_data
from dashboard.logic import (
    category_change,
    category_detail,
    category_overview,
    category_threshold_summary,
    enrich_segments,
    get_available_snapshot_dates,
    migration_summary,
    overview_metrics,
    previous_snapshot,
    product_ranking,
    scenario_summary,
    segment_summary,
    select_snapshot,
    seller_ranking,
    simulate_dynamic_commission,
    simulate_product_promotion,
    simulate_soft_penalty,
    top_destroyers,
    top_protectors,
    toxic_card,
)

st.set_page_config(page_title="FashionHero Margin Watch", page_icon="📉", layout="wide")


def badge_html(label: str, status: str) -> str:
    palette = {
        "healthy": ("#2f7d4a", "#e7f5ec"),
        "warning": ("#b26b00", "#fff3df"),
        "critical": ("#9e4040", "#fde8e8"),
    }
    fg, bg = palette[status]
    return (
        f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;"
        f"background:{bg};color:{fg};font-weight:600;font-size:0.85rem'>{label}: {status.upper()}</span>"
    )


def format_pln(value: float) -> str:
    return f"{value:,.0f} PLN".replace(",", " ")


def app() -> None:
    st.title("FashionHero Margin Watch")
    st.caption(
        "Decision dashboard for margin leakage, risky categories and preview interventions. Runtime reads only from the local SQLite snapshot built by the pipeline."
    )

    data = load_all_data()
    available_dates = get_available_snapshot_dates(data["user_agg_daily"])
    st.sidebar.header("Scenario controls")
    snapshot_date = st.sidebar.selectbox("Snapshot date", available_dates, index=len(available_dates) - 1)
    category_options = select_snapshot(data["category_agg_daily"], snapshot_date).sort_values("category_name")
    category_id = st.sidebar.selectbox(
        "Category drill-down",
        category_options["category_id"].tolist(),
        format_func=lambda item: category_options.loc[category_options["category_id"] == item, "category_name"].iloc[0],
    )

    soft_top_pct = st.sidebar.slider("Soft penalty target (%)", min_value=5, max_value=30, value=10, step=5)
    soft_return_reduction_pct = st.sidebar.slider("Soft penalty return-cost reduction (%)", 5, 40, value=18, step=1)
    soft_gmv_drag_pct = st.sidebar.slider("Soft penalty GMV drag (%)", 0, 10, value=4, step=1)
    commission_uplift_pp = st.sidebar.slider("Dynamic commission uplift (pp)", 1, 6, value=3, step=1)
    promotion_gmv_uplift_pct = st.sidebar.slider("Promotion GMV uplift (%)", 1, 10, value=5, step=1)

    latest_users = select_snapshot(data["user_agg_daily"], snapshot_date)
    latest_sellers = select_snapshot(data["seller_agg_daily"], snapshot_date)
    latest_products = select_snapshot(data["product_agg_daily"], snapshot_date)
    latest_categories = select_snapshot(data["category_agg_daily"], snapshot_date)
    latest_scenarios = select_snapshot(data["scenario_outputs_daily"], snapshot_date)
    prev_users = previous_snapshot(data["user_agg_daily"], snapshot_date)
    prev_categories = previous_snapshot(data["category_agg_daily"], snapshot_date)

    latest_users, latest_sellers = enrich_segments(latest_users, latest_sellers)
    prev_users, _ = enrich_segments(prev_users, latest_sellers) if not prev_users.empty else (prev_users, latest_sellers)

    metrics = overview_metrics(latest_sellers, latest_categories, latest_scenarios)
    toxic = toxic_card(latest_users)
    segment_table = segment_summary(latest_users)
    category_table = category_overview(latest_categories)
    seller_table = seller_ranking(latest_sellers)
    product_table = product_ranking(latest_products)
    movement = migration_summary(prev_users, latest_users)
    category_delta = category_change(prev_categories, latest_categories)
    selected_category = category_detail(category_id, latest_categories, latest_products, latest_sellers)
    product_destroyers, seller_destroyers = top_destroyers(latest_products, latest_sellers)
    product_protectors, seller_protectors = top_protectors(latest_products, latest_sellers)

    soft_penalty = simulate_soft_penalty(
        latest_users,
        top_pct=soft_top_pct,
        return_reduction_pct=soft_return_reduction_pct,
        gmv_drag_pct=soft_gmv_drag_pct,
    )
    dynamic_commission = simulate_dynamic_commission(
        latest_sellers,
        top_pct=20,
        uplift_pp=commission_uplift_pp,
        gmv_drag_pct=2,
    )
    product_promotion = simulate_product_promotion(
        latest_products,
        top_pct=25,
        gmv_uplift_pct=promotion_gmv_uplift_pct,
        conversion_uplift_pct=8,
    )

    render_overview(metrics, toxic, snapshot_date)
    render_where_we_lose_money(segment_table, category_table)
    render_category_drilldown(selected_category, category_delta)
    render_impact_views(product_destroyers, seller_destroyers, product_protectors, seller_protectors, seller_table, product_table)
    render_user_segments(latest_users, movement)
    render_simulator(soft_penalty, dynamic_commission, product_promotion)
    render_change_tracking(category_delta, latest_scenarios, data["interventions_log"])


def render_overview(metrics: dict[str, float], toxic: dict[str, float], snapshot_date) -> None:
    st.subheader("Executive overview")
    st.caption(f"30-day view as of {snapshot_date}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("GMV (30d)", format_pln(metrics["gmv"]))
    col2.metric("Return rate", f"{metrics['return_rate'] * 100:.1f}%")
    col3.metric("Margin contribution (30d)", format_pln(metrics["margin"]))
    col4.metric("Contribution / order", f"{metrics['contribution_per_order']:.1f} PLN")

    col5, col6 = st.columns(2)
    col5.metric("Top risk category", metrics["highest_risk_category_name"])
    col6.metric("Estimated margin headroom", format_pln(metrics["projected_margin_headroom"]))

    badge_row = " ".join(
        [
            badge_html("Margin", "healthy" if metrics["contribution_per_order"] >= 20 else "warning" if metrics["contribution_per_order"] >= 8 else "critical"),
            badge_html("Returns", "healthy" if metrics["return_rate"] <= 0.28 else "warning" if metrics["return_rate"] <= 0.4 else "critical"),
            badge_html("Toxic share", "healthy" if toxic["user_share_pct"] <= 12 else "warning" if toxic["user_share_pct"] <= 20 else "critical"),
        ]
    )
    st.markdown(badge_row, unsafe_allow_html=True)
    st.error(
        f"{toxic['user_share_pct']:.1f}% użytkowników generuje {toxic['return_cost_share_pct']:.1f}% kosztów zwrotów i ma ujemną marżę {toxic['margin_per_order']:.1f} PLN per order."
    )


def render_where_we_lose_money(segment_table: pd.DataFrame, category_table: pd.DataFrame) -> None:
    st.subheader("Where margin leaks")
    left, right = st.columns([1.2, 1])

    with left:
        formatted = segment_table.rename(
            columns={
                "segment_label": "segment",
                "users_pct": "% users",
                "gmv_pct": "% GMV",
                "return_cost_pct": "% return cost",
                "return_rate": "avg return rate",
                "margin": "margin",
                "margin_per_order": "margin / order",
            }
        )
        styled = formatted.style.format(
            {
                "% users": "{:.1f}%",
                "% GMV": "{:.1f}%",
                "% return cost": "{:.1f}%",
                "avg return rate": "{:.1%}",
                "margin": "{:.0f} PLN",
                "margin / order": "{:.1f} PLN",
            }
        ).apply(lambda row: ["background-color: #fde8e8" if row["segment"] == "toxic" else "" for _ in row], axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)

    with right:
        category_chart = px.bar(
            category_table,
            x="category_name",
            y="margin_contribution",
            color="health",
            color_discrete_map=CATEGORY_HEALTH_COLORS,
            hover_data={"return_rate_last_30d": ":.1%", "toxic_share": ":.1%"},
            labels={"category_name": "Category", "margin_contribution": "Margin contribution"},
        )
        category_chart.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(category_chart, use_container_width=True)


def render_category_drilldown(selected_category: dict[str, object], category_delta: pd.DataFrame) -> None:
    st.subheader("Category drill-down")
    summary = selected_category["summary"]
    products = selected_category["products"]
    sellers = selected_category["sellers"]
    thresholds = category_threshold_summary()

    metric1, metric2, metric3, metric4, metric5 = st.columns(5)
    metric1.metric("Category", str(summary["category_name"]))
    metric2.metric("GMV", format_pln(float(summary["gmv_last_30d"])))
    metric3.metric("Return rate", f"{float(summary['return_rate_last_30d']) * 100:.1f}%")
    metric4.metric("Contribution / order", f"{float(summary['contribution_per_order']):.1f} PLN")
    metric5.metric("Toxic share", f"{float(summary['toxic_share']) * 100:.1f}%")

    st.caption(
        f"Health thresholds: healthy returns <= {thresholds['healthy_return_rate_max']:.0%}, warning returns <= {thresholds['warning_return_rate_max']:.0%}, healthy contribution/order >= {thresholds['healthy_margin_per_order_min']:.0f} PLN."
    )

    left, right = st.columns(2)
    with left:
        st.markdown("**Products in category**")
        st.dataframe(
            products[["product_name", "product_segment", "orders", "return_rate", "margin_contribution", "promotion_score"]]
            .style.format({"orders": "{:.0f}", "return_rate": "{:.1%}", "margin_contribution": "{:.0f} PLN", "promotion_score": "{:.1f}"}),
            use_container_width=True,
            hide_index=True,
        )
    with right:
        st.markdown("**Sellers in category**")
        st.dataframe(
            sellers[["seller_name", "seller_segment", "gmv_last_30d", "return_rate_last_30d", "margin_contribution", "commission_tier"]]
            .style.format({"gmv_last_30d": "{:.0f} PLN", "return_rate_last_30d": "{:.1%}", "margin_contribution": "{:.0f} PLN"}),
            use_container_width=True,
            hide_index=True,
        )

    if not category_delta.empty:
        st.markdown("**Before / after change tracking by category**")
        st.dataframe(
            category_delta.style.format(
                {"gmv_delta": "{:+.0f} PLN", "margin_delta": "{:+.0f} PLN", "return_rate_delta": "{:+.1%}"}
            ),
            use_container_width=True,
            hide_index=True,
        )


def render_impact_views(
    product_destroyers: pd.DataFrame,
    seller_destroyers: pd.DataFrame,
    product_protectors: pd.DataFrame,
    seller_protectors: pd.DataFrame,
    seller_table: pd.DataFrame,
    product_table: pd.DataFrame,
) -> None:
    st.subheader("Seller / product impact")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Top destroyers**")
        destroyers = product_destroyers[["product_name", "return_rate", "margin_contribution"]].copy()
        destroyers["owner"] = "Product"
        seller_rows = seller_destroyers[["seller_name", "return_rate_last_30d", "margin_contribution"]].rename(
            columns={"seller_name": "product_name", "return_rate_last_30d": "return_rate"}
        )
        seller_rows["owner"] = "Seller"
        st.dataframe(
            pd.concat([destroyers, seller_rows], ignore_index=True)
            .style.format({"return_rate": "{:.1%}", "margin_contribution": "{:.0f} PLN"}),
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        st.markdown("**Top protectors**")
        protectors = product_protectors[["product_name", "return_rate", "margin_contribution"]].copy()
        protectors["owner"] = "Product"
        seller_rows = seller_protectors[["seller_name", "return_rate_last_30d", "margin_contribution"]].rename(
            columns={"seller_name": "product_name", "return_rate_last_30d": "return_rate"}
        )
        seller_rows["owner"] = "Seller"
        st.dataframe(
            pd.concat([protectors, seller_rows], ignore_index=True)
            .style.format({"return_rate": "{:.1%}", "margin_contribution": "{:.0f} PLN"}),
            use_container_width=True,
            hide_index=True,
        )

    seller_chart = px.bar(
        seller_table.head(6),
        x="seller_name",
        y="margin_contribution",
        color="seller_segment",
        color_discrete_map=SELLER_SEGMENT_COLORS,
    )
    seller_chart.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))

    product_chart = px.scatter(
        product_table.head(12),
        x="return_rate",
        y="margin_contribution",
        size="orders",
        color="product_segment",
        hover_name="product_name",
    )
    product_chart.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))

    left, right = st.columns(2)
    left.plotly_chart(seller_chart, use_container_width=True)
    right.plotly_chart(product_chart, use_container_width=True)


def render_user_segments(users_df: pd.DataFrame, movement: pd.DataFrame) -> None:
    st.subheader("User segments")
    scatter = px.scatter(
        users_df,
        x="return_rate_last_30d",
        y="gmv_last_30d",
        color="segment_label",
        size="orders_last_30d",
        hover_name="user_name",
        hover_data={
            "primary_device": True,
            "contribution_margin_last_30d": True,
            "return_cost_last_30d": True,
            "quarter_returns_count": True,
            "return_rate_last_30d": ":.1%",
        },
        color_discrete_map=USER_SEGMENT_COLORS,
        labels={"return_rate_last_30d": "Return rate (30d)", "gmv_last_30d": "GMV (30d)"},
    )
    scatter.add_vline(x=0.35, line_dash="dot", line_color="#7d756b")
    scatter.add_hline(y=900, line_dash="dot", line_color="#7d756b")
    scatter.update_layout(height=430, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(scatter, use_container_width=True)

    if movement.empty:
        st.info("No previous snapshot available for migration tracking yet.")
    else:
        top_moves = movement.head(6).copy()
        top_moves["move"] = top_moves["from_segment"] + " → " + top_moves["to_segment"]
        st.dataframe(top_moves[["move", "users"]], use_container_width=True, hide_index=True)


def render_simulation_card(title: str, simulation: dict[str, object], affected_label: str) -> None:
    st.markdown(f"**{title}**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Estimated margin delta", format_pln(float(simulation["delta_margin"])))
    col2.metric("Estimated GMV delta", format_pln(float(simulation["delta_gmv"])))
    col3.metric(affected_label, int(simulation[affected_label.lower().replace(" ", "_")]))
    st.dataframe(
        simulation["targeted_entities"].style.format(
            {column: "{:.0f} PLN" for column in simulation["targeted_entities"].columns if "gmv" in column or "margin" in column}
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_simulator(soft_penalty: dict[str, object], dynamic_commission: dict[str, object], product_promotion: dict[str, object]) -> None:
    st.subheader("Intervention simulator")
    st.caption("All values below are directional estimates. They are meant to support a decision, not replace experiment measurement.")

    tabs = st.tabs(["Soft penalty", "Dynamic commission", "Promote low-return products"])
    with tabs[0]:
        render_simulation_card(soft_penalty["label"], soft_penalty, "Affected users")
    with tabs[1]:
        render_simulation_card(dynamic_commission["label"], dynamic_commission, "Affected sellers")
    with tabs[2]:
        render_simulation_card(product_promotion["label"], product_promotion, "Affected products")


def render_change_tracking(category_delta: pd.DataFrame, scenarios_df: pd.DataFrame, interventions_df: pd.DataFrame) -> None:
    st.subheader("Change tracking")
    left, right = st.columns(2)

    with left:
        st.markdown("**Scenario output history**")
        st.dataframe(
            scenario_summary(scenarios_df).style.format(
                {"delta_margin": "{:.0f} PLN", "delta_gmv": "{:.0f} PLN", "observed_delta": "{:.2%}"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.markdown("**Interventions log**")
        st.dataframe(
            interventions_df[["intervention_id", "intervention_code", "target_type", "target_id", "status", "start_date", "end_date"]],
            use_container_width=True,
            hide_index=True,
        )

    if not category_delta.empty:
        chart = go.Figure()
        chart.add_trace(go.Bar(name="Margin delta", x=category_delta["category_name"], y=category_delta["margin_delta"]))
        chart.add_trace(go.Scatter(name="Return rate delta", x=category_delta["category_name"], y=category_delta["return_rate_delta"], yaxis="y2"))
        chart.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(title="Margin delta"),
            yaxis2=dict(title="Return rate delta", overlaying="y", side="right", tickformat=".0%"),
        )
        st.plotly_chart(chart, use_container_width=True)


if __name__ == "__main__":
    app()
