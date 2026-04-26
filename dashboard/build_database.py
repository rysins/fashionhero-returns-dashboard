from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
SEED_DIR = BASE_DIR / "seeds"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "fashionhero_dashboard.sqlite"

SNAPSHOT_DATES = ("2026-03-28", "2026-04-27")
RANDOM_SEED = 42

SELLER_PROFILES = {
    "S001": {"category": "shoes", "traffic": ["direct", "search", "email"]},
    "S002": {"category": "dresses", "traffic": ["direct", "email", "search"]},
    "S003": {"category": "knitwear", "traffic": ["search", "instagram", "email"]},
    "S004": {"category": "handmade_shoes", "traffic": ["direct", "search"]},
    "S005": {"category": "basics", "traffic": ["email", "direct", "social"]},
    "S006": {"category": "shoes", "traffic": ["sale_push", "instagram", "google_shopping"]},
    "S007": {"category": "dresses", "traffic": ["google_shopping", "sale_push", "instagram"]},
    "S008": {"category": "occasionwear", "traffic": ["instagram", "google_shopping", "social"]},
}

SEGMENT_SELLER_WEIGHTS = {
    "toxic": [("S007", 0.30), ("S006", 0.28), ("S008", 0.22), ("S003", 0.12), ("S002", 0.08)],
    "high_value": [("S001", 0.32), ("S002", 0.24), ("S004", 0.18), ("S005", 0.18), ("S003", 0.08)],
    "tryers": [("S002", 0.20), ("S003", 0.20), ("S005", 0.20), ("S006", 0.20), ("S008", 0.20)],
    "low_value": [("S005", 0.32), ("S001", 0.20), ("S004", 0.16), ("S003", 0.16), ("S002", 0.16)],
}

RETURN_REASONS = {
    "toxic": ["size mismatch", "ordered multiple sizes", "looked different in person", "too expensive to keep"],
    "high_value": ["quality issue", "gift return", "late delivery"],
    "tryers": ["wrong fit", "changed mind", "late delivery"],
    "low_value": ["wrong fit", "changed mind", "material feel"],
}


@dataclass
class UserSeed:
    user_id: str
    user_name: str
    segment_label: str
    primary_device: str
    avg_items_per_order: float
    avg_gmv_per_order: float
    return_rate: float


def load_seed_table(name: str) -> pd.DataFrame:
    return pd.read_csv(SEED_DIR / f"{name}.csv")


def weighted_choice(randomizer: random.Random, weighted_values: list[tuple[str, float]]) -> str:
    values = [value for value, _ in weighted_values]
    weights = [weight for _, weight in weighted_values]
    return randomizer.choices(values, weights=weights, k=1)[0]


def build_synthetic_orders() -> pd.DataFrame:
    randomizer = random.Random(RANDOM_SEED)
    seed_users = load_seed_table("user_agg_daily")
    latest_users = seed_users.loc[seed_users["date"] == SNAPSHOT_DATES[-1]].copy()

    seeds = [
        UserSeed(
            user_id=row.user_id,
            user_name=row.user_name,
            segment_label=row.segment_label,
            primary_device=row.primary_device,
            avg_items_per_order=float(row.avg_items_per_order),
            avg_gmv_per_order=float(row.gmv_last_30d) / max(int(row.orders_last_30d), 1),
            return_rate=float(row.return_rate_last_30d),
        )
        for row in latest_users.itertuples(index=False)
    ]

    records: list[dict[str, object]] = []
    synthetic_index = 2000

    for seed in seeds:
        synthetic_orders_count = 8 if seed.segment_label in {"toxic", "high_value"} else 5
        for order_number in range(synthetic_orders_count):
            synthetic_index += 1
            seller_id = weighted_choice(randomizer, SEGMENT_SELLER_WEIGHTS[seed.segment_label])
            seller_profile = SELLER_PROFILES[seller_id]
            month = 2 if order_number < 2 else 3 if order_number < 4 else 4
            day = randomizer.randint(1, 27)
            order_date = pd.Timestamp(year=2026, month=month, day=day).date().isoformat()
            avg_gmv = seed.avg_gmv_per_order
            gmv = round(max(90, randomizer.gauss(avg_gmv, avg_gmv * 0.18)), 2)
            returned_flag = 1 if randomizer.random() < seed.return_rate else 0
            if seed.segment_label == "toxic" and order_number % 3 == 0:
                returned_flag = 1
            items_count = max(1, round(randomizer.gauss(seed.avg_items_per_order, 0.6)))
            return_value = round(gmv * randomizer.uniform(0.45, 1.0), 2) if returned_flag else 0.0
            return_reason = randomizer.choice(RETURN_REASONS[seed.segment_label]) if returned_flag else ""
            return_date = (
                pd.Timestamp(order_date) + pd.Timedelta(days=randomizer.randint(4, 11))
            ).date().isoformat() if returned_flag else ""
            traffic_source = randomizer.choice(seller_profile["traffic"])
            if seed.primary_device == "desktop" and traffic_source == "sale_push":
                traffic_source = "email"

            records.append(
                {
                    "order_id": f"SYN{synthetic_index}",
                    "user_id": seed.user_id,
                    "seller_id": seller_id,
                    "order_date": order_date,
                    "gmv": round(gmv, 2),
                    "commission": round(gmv * 0.22, 2),
                    "returned_flag": returned_flag,
                    "return_value": round(return_value, 2),
                    "return_reason": return_reason,
                    "return_date": return_date,
                    "items_count": items_count,
                    "category": seller_profile["category"],
                    "device": seed.primary_device,
                    "traffic_source": traffic_source,
                }
            )

    return pd.DataFrame.from_records(records)


def configure_database(connection: sqlite3.Connection) -> None:
    connection.execute("pragma journal_mode = wal;")
    connection.execute("pragma synchronous = normal;")
    connection.execute("pragma foreign_keys = on;")


def create_indexes(connection: sqlite3.Connection) -> None:
    statements = [
        "create index if not exists idx_orders_fact_user_date on orders_fact (user_id, order_date);",
        "create index if not exists idx_orders_fact_seller_date on orders_fact (seller_id, order_date);",
        "create index if not exists idx_user_agg_daily_user_date on user_agg_daily (user_id, date);",
        "create index if not exists idx_seller_agg_daily_seller_date on seller_agg_daily (seller_id, date);",
        "create index if not exists idx_product_agg_daily_product_date on product_agg_daily (product_id, date);",
        "create index if not exists idx_interventions_log_target on interventions_log (target_type, target_id);",
    ]
    for statement in statements:
        connection.execute(statement)


def build_database() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    orders_seed = load_seed_table("orders_fact")
    synthetic_orders = build_synthetic_orders()
    all_orders = pd.concat([orders_seed, synthetic_orders], ignore_index=True)

    with sqlite3.connect(DB_PATH) as connection:
        configure_database(connection)
        all_orders.to_sql("orders_fact", connection, index=False, if_exists="replace")
        load_seed_table("user_agg_daily").to_sql("user_agg_daily", connection, index=False, if_exists="replace")
        load_seed_table("seller_agg_daily").to_sql("seller_agg_daily", connection, index=False, if_exists="replace")
        load_seed_table("product_agg_daily").to_sql("product_agg_daily", connection, index=False, if_exists="replace")
        load_seed_table("interventions_log").to_sql("interventions_log", connection, index=False, if_exists="replace")
        create_indexes(connection)

    return DB_PATH


def build_database_if_missing() -> Path:
    if not DB_PATH.exists():
        return build_database()
    return DB_PATH


if __name__ == "__main__":
    print(f"Built database at {build_database()}")
