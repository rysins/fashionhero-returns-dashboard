from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.build_database import DB_PATH, build_database
from dashboard.loaders import load_all_data
from dashboard.logic import (
    enrich_segments,
    get_available_snapshot_dates,
    overview_metrics,
    previous_snapshot,
    segment_summary,
    select_snapshot,
    simulate_top_returner_intervention,
    toxic_card,
)


def main() -> None:
    build_database()
    data = load_all_data()
    dates = get_available_snapshot_dates(data["user_agg_daily"])
    latest_date = dates[-1]
    users = select_snapshot(data["user_agg_daily"], latest_date)
    sellers = select_snapshot(data["seller_agg_daily"], latest_date)
    previous_users = previous_snapshot(data["user_agg_daily"], latest_date)

    users, sellers = enrich_segments(users, sellers)
    metrics = overview_metrics(sellers)
    segments = segment_summary(users)
    toxic = toxic_card(users)
    simulation = simulate_top_returner_intervention(users, top_pct=10, return_reduction_pct=15, gmv_drop_pct=3)

    assert metrics["gmv"] > 0
    assert metrics["margin"] != 0
    assert len(data["orders_fact"]) > 33
    assert "toxic" in segments["segment_label"].tolist()
    assert toxic["margin_per_order"] < 0
    assert simulation["affected_users"] >= 1
    assert not previous_users.empty
    assert DB_PATH.exists()

    print("Dashboard validation passed.")


if __name__ == "__main__":
    main()
