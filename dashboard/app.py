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

from dashboard.config import (
    SELLER_SEGMENT_COLORS,
    USER_SEGMENT_COLORS,
    margin_health_badge,
    return_rate_badge,
    toxic_order_share_badge,
)
from dashboard.loaders import load_all_data
from dashboard.logic import (
    enrich_segments,
    get_available_snapshot_dates,
    migration_summary,
    overview_metrics,
    previous_snapshot,
    segment_summary,
    select_snapshot,
    seller_ranking,
    simulate_top_returner_intervention,
    toxic_card,
)

st.set_page_config(
    page_title="FashionHero Margin Watch",
    page_icon="📉",
    layout="wide",
)


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
        "Internal MVP built on mock data. The purpose is to expose where margin is leaking, which cohorts are toxic, and what a simple intervention could change."
    )

    data = load_all_data()
    available_dates = get_available_snapshot_dates(data["user_agg_daily"])
    st.sidebar.header("Scenario controls")
    snapshot_date = st.sidebar.selectbox("Snapshot date", available_dates, index=len(available_dates) - 1)
    top_pct = st.sidebar.slider("Target top returners (%)", min_value=5, max_value=40, value=10, step=5)
    return_reduction_pct = st.sidebar.slider(
        "Assumed reduction in return costs (%)", min_value=5, max_value=35, value=15, step=5
    )
    gmv_drop_pct = st.sidebar.slider(
        "Assumed GMV drag from intervention (%)", min_value=0, max_value=10, value=3, step=1
    )
    st.sidebar.caption(
        "Simulation is heuristic. It estimates avoided return cost minus lost commission on GMV that may disappear after a stricter intervention."
    )

    latest_users = select_snapshot(data["user_agg_daily"], snapshot_date)
    latest_sellers = select_snapshot(data["seller_agg_daily"], snapshot_date)
    prev_users = previous_snapshot(data["user_agg_daily"], snapshot_date)

    latest_users, latest_sellers = enrich_segments(latest_users, latest_sellers)
    prev_users, _ = enrich_segments(prev_users, latest_sellers) if not prev_users.empty else (prev_users, latest_sellers)

    metrics = overview_metrics(latest_sellers)
    toxic = toxic_card(latest_users)
    segment_table = segment_summary(latest_users)
    seller_table = seller_ranking(latest_sellers)
    movement = migration_summary(prev_users, latest_users)
    simulation = simulate_top_returner_intervention(
        latest_users,
        top_pct=top_pct,
        return_reduction_pct=return_reduction_pct,
        gmv_drop_pct=gmv_drop_pct,
    )

    render_overview(metrics, toxic, snapshot_date)
    render_where_we_lose_money(segment_table)
    render_user_segments(latest_users, movement)
    render_seller_segments(seller_table)
    render_simulation(simulation, top_pct, return_reduction_pct, gmv_drop_pct)
    render_interventions(data["interventions_log"])


def render_overview(metrics: dict[str, float], toxic: dict[str, float], snapshot_date) -> None:
    st.subheader("Overview")
    st.caption(f"30-day view as of {snapshot_date}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("GMV (30d)", format_pln(metrics["gmv"]))
    col2.metric("Return rate", f"{metrics['return_rate'] * 100:.1f}%")
    col3.metric("Margin contribution (30d)", format_pln(metrics["margin"]))
    col4.metric("Contribution / order", f"{metrics['contribution_per_order']:.1f} PLN")

    badge_row = " ".join(
        [
            badge_html("Margin", margin_health_badge(metrics["contribution_per_order"])),
            badge_html("Returns", return_rate_badge(metrics["return_rate"])),
            badge_html("Toxic share", toxic_order_share_badge(toxic["user_share_pct"] / 100)),
        ]
    )
    st.markdown(badge_row, unsafe_allow_html=True)

    st.error(
        f"{toxic['user_share_pct']:.1f}% użytkowników generuje {toxic['return_cost_share_pct']:.1f}% kosztów zwrotów "
        f"i ma ujemną marżę {toxic['margin_per_order']:.1f} PLN per order."
    )


def render_where_we_lose_money(segment_table: pd.DataFrame) -> None:
    st.subheader("Where we lose money")
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
    ).apply(
        lambda row: ["background-color: #fde8e8" if row["segment"] == "toxic" else "" for _ in row],
        axis=1,
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)


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
            "return_rate_last_30d": ":.1%",
        },
        color_discrete_map=USER_SEGMENT_COLORS,
        labels={
            "return_rate_last_30d": "Return rate (30d)",
            "gmv_last_30d": "GMV (30d)",
            "segment_label": "Segment",
        },
    )
    scatter.add_vline(x=0.35, line_dash="dot", line_color="#7d756b")
    scatter.add_hline(y=900, line_dash="dot", line_color="#7d756b")
    scatter.update_layout(height=450, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(scatter, use_container_width=True)

    left, right = st.columns([1.2, 1])
    with left:
        st.caption("Quadrants are intentionally simple: high GMV + low returns is the zone to protect. High returns + high GMV is where interventions matter most.")
    with right:
        if movement.empty:
            st.info("No previous snapshot available for migration tracking yet.")
        else:
            top_moves = movement.head(4).copy()
            top_moves["move"] = top_moves["from_segment"] + " → " + top_moves["to_segment"]
            st.dataframe(top_moves[["move", "users"]], use_container_width=True, hide_index=True)


def render_seller_segments(seller_table: pd.DataFrame) -> None:
    st.subheader("Seller segments")
    st.dataframe(
        seller_table.style.format(
            {
                "gmv_last_30d": "{:.0f} PLN",
                "return_rate_last_30d": "{:.1%}",
                "margin_contribution": "{:.0f} PLN",
                "avg_order_value": "{:.0f} PLN",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    risk_chart = px.bar(
        seller_table.head(6),
        x="seller_name",
        y="margin_contribution",
        color="seller_segment",
        color_discrete_map=SELLER_SEGMENT_COLORS,
        labels={"seller_name": "Seller", "margin_contribution": "Margin contribution (30d)"},
    )
    risk_chart.update_layout(height=360, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(risk_chart, use_container_width=True)


def render_simulation(simulation: dict[str, object], top_pct: int, return_reduction_pct: int, gmv_drop_pct: int) -> None:
    st.subheader("Simulation")
    st.caption(
        f"Scenario: intervene on the top {top_pct}% returners, reduce their return-cost burden by {return_reduction_pct}% and assume {gmv_drop_pct}% GMV drag."
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Estimated margin delta", format_pln(float(simulation["delta_margin"])))
    m2.metric("Estimated GMV delta", format_pln(float(simulation["delta_gmv"])))
    m3.metric("Affected users", int(simulation["affected_users"]))

    chart = go.Figure(
        data=[
            go.Bar(
                x=["Return-cost saved", "Lost commission", "Net margin delta"],
                y=[
                    float(simulation["return_cost_saved"]),
                    -float(simulation["lost_commission"]),
                    float(simulation["delta_margin"]),
                ],
                marker_color=["#2f7d4a", "#9e4040", "#1b1b1b"],
            )
        ]
    )
    chart.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="PLN")
    st.plotly_chart(chart, use_container_width=True)

    st.dataframe(
        simulation["targeted_users"].style.format(
            {
                "gmv_last_30d": "{:.0f} PLN",
                "return_rate_last_30d": "{:.1%}",
                "return_cost_last_30d": "{:.0f} PLN",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Estimate only. This is a directional decision tool, not a production forecast.")


def render_interventions(interventions_df: pd.DataFrame) -> None:
    with st.expander("Interventions log"):
        st.dataframe(interventions_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    app()
