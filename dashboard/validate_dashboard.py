from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.build_database import DB_PATH, build_database
from dashboard.loaders import load_all_data
from dashboard.logic import (
    category_detail,
    category_overview,
    enrich_segments,
    get_available_snapshot_dates,
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
    toxic_card,
)


def main() -> None:
    build_database()
    data = load_all_data()
    dates = get_available_snapshot_dates(data["user_agg_daily"])
    latest_date = dates[-1]

    users = select_snapshot(data["user_agg_daily"], latest_date)
    sellers = select_snapshot(data["seller_agg_daily"], latest_date)
    products = select_snapshot(data["product_agg_daily"], latest_date)
    categories = select_snapshot(data["category_agg_daily"], latest_date)
    previous_users = previous_snapshot(data["user_agg_daily"], latest_date)
    scenarios = select_snapshot(data["scenario_outputs_daily"], latest_date)

    users, sellers = enrich_segments(users, sellers)
    metrics = overview_metrics(sellers, categories, scenarios)
    segments = segment_summary(users)
    toxic = toxic_card(users)
    category_summary = category_overview(categories)
    detail = category_detail(category_summary.iloc[0]["category_id"], categories, products, sellers)
    soft_penalty = simulate_soft_penalty(users, top_pct=10, return_reduction_pct=18, gmv_drag_pct=4)
    dynamic_commission = simulate_dynamic_commission(sellers, top_pct=20, uplift_pp=3, gmv_drag_pct=2)
    product_promotion = simulate_product_promotion(products, top_pct=25, gmv_uplift_pct=5, conversion_uplift_pct=8)

    assert metrics["gmv"] > 0
    assert metrics["margin"] != 0
    assert len(data["orders_fact"]) > 33
    assert "toxic" in segments["segment_label"].tolist()
    assert toxic["margin_per_order"] < 0
    assert soft_penalty["affected_users"] >= 1
    assert dynamic_commission["affected_sellers"] >= 1
    assert product_promotion["affected_products"] >= 1
    assert not previous_users.empty
    assert DB_PATH.exists()
    assert not detail["products"].empty
    assert not detail["sellers"].empty
    assert not scenario_summary(scenarios).empty

    print("Dashboard validation passed.")


if __name__ == "__main__":
    main()
