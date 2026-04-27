from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random
import sqlite3

import pandas as pd

from dashboard.config import INTERVENTION_CONFIG

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE_DIR = BASE_DIR / "seeds"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "fashionhero_dashboard.sqlite"
MANIFEST_PATH = DATA_DIR / "pipeline_manifest.json"
SNAPSHOT_DATES = ("2026-03-28", "2026-04-27")
RANDOM_SEED = 42

REQUIRED_SOURCE_COLUMNS = {
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


@dataclass(frozen=True)
class PipelineRunManifest:
    snapshot_date: str
    source_dir: str
    validation_status: str
    record_counts: dict[str, int]
    rejected_records: int


@dataclass(frozen=True)
class UserSeed:
    user_id: str
    user_name: str
    segment_label: str
    primary_device: str
    avg_items_per_order: float
    avg_gmv_per_order: float
    return_rate: float


class CSVSnapshotAdapter:
    def __init__(self, source_dir: Path) -> None:
        self.source_dir = source_dir

    def load_table(self, name: str) -> pd.DataFrame:
        dataframe = pd.read_csv(self.source_dir / f"{name}.csv")
        missing = [column for column in REQUIRED_SOURCE_COLUMNS[name] if column not in dataframe.columns]
        if missing:
            raise ValueError(f"{name} is missing required columns: {', '.join(missing)}")
        return dataframe

    def load_all(self) -> dict[str, pd.DataFrame]:
        return {name: self.load_table(name) for name in REQUIRED_SOURCE_COLUMNS}


def slugify_category(value: str) -> str:
    return value.lower().replace(" ", "_").replace("&", "and")


def weighted_choice(randomizer: random.Random, weighted_values: list[tuple[str, float]]) -> str:
    values = [value for value, _ in weighted_values]
    weights = [weight for _, weight in weighted_values]
    return randomizer.choices(values, weights=weights, k=1)[0]


def build_product_lookup(products_df: pd.DataFrame) -> dict[tuple[str, str], list[dict[str, str]]]:
    lookup: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in products_df.itertuples(index=False):
        key = (row.seller_id, row.category)
        lookup.setdefault(key, []).append({"product_id": row.product_id, "product_name": row.product_name})
    return lookup


def build_synthetic_orders(users_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    randomizer = random.Random(RANDOM_SEED)
    latest_users = users_df.loc[users_df["date"] == SNAPSHOT_DATES[-1]].copy()
    product_lookup = build_product_lookup(products_df)

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
            order_date = pd.Timestamp(year=2026, month=month, day=day)
            avg_gmv = seed.avg_gmv_per_order
            gmv = round(max(90, randomizer.gauss(avg_gmv, avg_gmv * 0.18)), 2)
            returned_flag = 1 if randomizer.random() < seed.return_rate else 0
            if seed.segment_label == "toxic" and order_number % 3 == 0:
                returned_flag = 1
            items_count = max(1, round(randomizer.gauss(seed.avg_items_per_order, 0.6)))
            return_value = round(gmv * randomizer.uniform(0.45, 1.0), 2) if returned_flag else 0.0
            return_reason = randomizer.choice(RETURN_REASONS[seed.segment_label]) if returned_flag else ""
            return_date = (
                order_date + pd.Timedelta(days=randomizer.randint(4, 11))
            ).date().isoformat() if returned_flag else ""
            traffic_source = randomizer.choice(seller_profile["traffic"])
            if seed.primary_device == "desktop" and traffic_source == "sale_push":
                traffic_source = "email"

            product_candidates = product_lookup.get((seller_id, seller_profile["category"])) or next(iter(product_lookup.values()))
            selected_product = randomizer.choice(product_candidates)

            records.append(
                {
                    "order_id": f"SYN{synthetic_index}",
                    "user_id": seed.user_id,
                    "seller_id": seller_id,
                    "product_id": selected_product["product_id"],
                    "product_name": selected_product["product_name"],
                    "order_date": order_date.date().isoformat(),
                    "delivered_at": (order_date + pd.Timedelta(days=3)).date().isoformat(),
                    "snapshot_date": SNAPSHOT_DATES[-1],
                    "gmv": round(gmv, 2),
                    "commission": round(gmv * 0.22, 2),
                    "effective_commission_rate": 0.22,
                    "returned_flag": returned_flag,
                    "return_value": round(return_value, 2),
                    "return_shipping_cost": 14.0 if returned_flag else 0.0,
                    "return_reason": return_reason,
                    "return_date": return_date,
                    "items_count": items_count,
                    "category": seller_profile["category"],
                    "category_id": slugify_category(seller_profile["category"]),
                    "device": seed.primary_device,
                    "traffic_source": traffic_source,
                }
            )

    return pd.DataFrame.from_records(records)


def normalize_orders(raw_orders: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    orders = raw_orders.copy()
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["return_date"] = pd.to_datetime(orders["return_date"], errors="coerce")
    orders["snapshot_date"] = SNAPSHOT_DATES[-1]
    orders["delivered_at"] = orders["order_date"] + pd.Timedelta(days=3)
    orders["category_id"] = orders["category"].map(slugify_category)
    orders["return_shipping_cost"] = orders["returned_flag"].astype(float) * 14.0
    orders["effective_commission_rate"] = (orders["commission"] / orders["gmv"]).fillna(0).round(4)

    product_lookup = build_product_lookup(products_df)
    assigned_ids: list[str] = []
    assigned_names: list[str] = []
    lookup_counters: dict[tuple[str, str], int] = {}
    fallback = products_df.iloc[0]

    for row in orders.itertuples(index=False):
        key = (row.seller_id, row.category)
        candidates = product_lookup.get(key)
        if not candidates:
            assigned_ids.append(str(fallback.product_id))
            assigned_names.append(str(fallback.product_name))
            continue
        index = lookup_counters.get(key, 0) % len(candidates)
        lookup_counters[key] = index + 1
        assigned_ids.append(candidates[index]["product_id"])
        assigned_names.append(candidates[index]["product_name"])

    orders["product_id"] = assigned_ids
    orders["product_name"] = assigned_names
    return orders


def normalize_users(users_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
    users = users_df.copy()
    users["snapshot_date"] = users["date"]
    users["user_segment_version"] = "v2"
    users["quarter_returns_count"] = 0
    users["free_return_eligibility"] = "eligible"

    for row in users.itertuples():
        window_end = pd.Timestamp(row.date)
        quarter_start = window_end - pd.Timedelta(days=90)
        returns_count = orders_df.loc[
            (orders_df["user_id"] == row.user_id)
            & (orders_df["returned_flag"] == 1)
            & (orders_df["order_date"] >= quarter_start)
            & (orders_df["order_date"] <= window_end),
        ].shape[0]
        users.loc[row.Index, "quarter_returns_count"] = returns_count
        users.loc[row.Index, "free_return_eligibility"] = "paid_after_threshold" if returns_count > 2 else "eligible"

    return users


def normalize_sellers(sellers_df: pd.DataFrame) -> pd.DataFrame:
    sellers = sellers_df.copy()
    sellers["snapshot_date"] = sellers["date"]
    sellers["seller_segment_version"] = "v2"
    sellers["effective_commission_rate"] = sellers["seller_id"].map(
        {
            "S001": 0.18,
            "S002": 0.19,
            "S003": 0.22,
            "S004": 0.22,
            "S005": 0.22,
            "S006": 0.21,
            "S007": 0.17,
            "S008": 0.20,
        }
    ).fillna(0.22)
    sellers["commission_tier"] = sellers["effective_commission_rate"].apply(
        lambda value: "negotiated" if value < 0.20 else "standard" if value <= 0.22 else "uplifted"
    )
    return sellers


def normalize_products(products_df: pd.DataFrame, sellers_df: pd.DataFrame) -> pd.DataFrame:
    products = products_df.copy()
    seller_commission = sellers_df[["seller_id", "date", "effective_commission_rate"]]
    products = products.merge(seller_commission, on=["seller_id", "date"], how="left")
    products["snapshot_date"] = products["date"]
    products["category_id"] = products["category"].map(slugify_category)
    products["gross_gmv"] = products["avg_price"] * products["orders"]
    products["return_cost_estimate"] = products["gross_gmv"] * products["return_rate"]
    products["margin_contribution"] = (
        products["gross_gmv"] * products["effective_commission_rate"] - products["return_cost_estimate"]
    ).round(1)
    guardrail = INTERVENTION_CONFIG["promote_low_return_products"]["return_rate_guardrail"]
    products["promotion_score"] = (
        (1 - products["return_rate"]) * 100
        + products["conversion_rate"] * 1000
        + (products["margin_contribution"] / products["orders"].replace(0, pd.NA)).fillna(0)
        + (products["return_rate"] <= guardrail).astype(int) * 12
    ).round(1)
    return products.drop(columns=["gross_gmv", "return_cost_estimate"])


def normalize_interventions(interventions_df: pd.DataFrame) -> pd.DataFrame:
    interventions = interventions_df.copy()
    mapping = {
        "ranking_change": ("promote_low_return_products", 1, "active"),
        "commission_increase": ("dynamic_commission_high_return_sellers", 1, "active"),
    }
    codes: list[str] = []
    versions: list[int] = []
    statuses: list[str] = []
    rules: list[str] = []
    parameter_json: list[str] = []

    for row in interventions.itertuples(index=False):
        code, version, status = mapping.get(row.type, ("soft_penalty_high_returners", 1, "planned"))
        config = INTERVENTION_CONFIG[code]
        codes.append(code)
        versions.append(version)
        statuses.append(status)
        rules.append(f"target={row.target_type};id={row.target_id}")
        parameter_json.append(json.dumps(config, sort_keys=True))

    interventions["intervention_code"] = codes
    interventions["version"] = versions
    interventions["status"] = statuses
    interventions["eligibility_rule"] = rules
    interventions["parameter_json"] = parameter_json
    return interventions


def build_category_agg(orders_df: pd.DataFrame, users_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    categories: list[dict[str, object]] = []
    product_snapshot = products_df[["date", "category", "margin_contribution", "orders"]]

    for snapshot_date in SNAPSHOT_DATES:
        snapshot_ts = pd.Timestamp(snapshot_date)
        window_start = snapshot_ts - pd.Timedelta(days=30)
        window_orders = orders_df.loc[(orders_df["order_date"] > window_start) & (orders_df["order_date"] <= snapshot_ts)].copy()
        user_snapshot = users_df.loc[users_df["date"] == snapshot_date, ["user_id", "segment_label"]]
        window_orders = window_orders.merge(user_snapshot, on="user_id", how="left")
        toxic_orders = window_orders.assign(toxic_order=(window_orders["segment_label"] == "toxic").astype(int))
        margin_by_category = product_snapshot.loc[product_snapshot["date"] == snapshot_date].groupby("category", as_index=False).agg(
            margin_contribution=("margin_contribution", "sum"),
            product_orders=("orders", "sum"),
        )
        grouped = toxic_orders.groupby(["category", "category_id"], as_index=False).agg(
            gmv_last_30d=("gmv", "sum"),
            orders_count=("order_id", "count"),
            return_rate_last_30d=("returned_flag", "mean"),
            toxic_orders=("toxic_order", "sum"),
        )
        grouped = grouped.merge(margin_by_category, on="category", how="left")
        grouped["margin_contribution"] = grouped["margin_contribution"].fillna(grouped["gmv_last_30d"] * 0.12)
        grouped["contribution_per_order"] = (
            grouped["margin_contribution"] / grouped["orders_count"].replace(0, pd.NA)
        ).fillna(0).round(1)
        grouped["toxic_share"] = (grouped["toxic_orders"] / grouped["orders_count"].replace(0, pd.NA)).fillna(0).round(3)
        grouped["snapshot_date"] = snapshot_date
        grouped["date"] = snapshot_date
        grouped["category_name"] = grouped["category"].str.title()
        categories.extend(grouped.to_dict(orient="records"))

    return pd.DataFrame(categories)[
        [
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
        ]
    ]


def _hash_scenario(snapshot_date: str, intervention_code: str, payload: dict[str, object]) -> str:
    serialised = json.dumps({"snapshot_date": snapshot_date, "code": intervention_code, **payload}, sort_keys=True)
    return hashlib.sha1(serialised.encode()).hexdigest()[:12]


def build_scenario_outputs(users_df: pd.DataFrame, sellers_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for snapshot_date in SNAPSHOT_DATES:
        snapshot_users = users_df.loc[users_df["date"] == snapshot_date].copy()
        snapshot_sellers = sellers_df.loc[sellers_df["date"] == snapshot_date].copy()
        snapshot_products = products_df.loc[products_df["date"] == snapshot_date].copy()

        user_top_pct = INTERVENTION_CONFIG["soft_penalty_high_returners"]["top_pct"]
        targeted_users = snapshot_users.sort_values(
            ["return_cost_last_30d", "return_rate_last_30d"], ascending=[False, False]
        ).head(max(1, round(len(snapshot_users) * user_top_pct / 100)))
        user_return_savings = targeted_users["return_cost_last_30d"].sum() * (
            INTERVENTION_CONFIG["soft_penalty_high_returners"]["return_cost_reduction_pct"] / 100
        )
        user_gmv_drag = targeted_users["gmv_last_30d"].sum() * (
            INTERVENTION_CONFIG["soft_penalty_high_returners"]["gmv_drag_pct"] / 100
        )
        payload = {
            "delta_margin": round(float(user_return_savings - user_gmv_drag * 0.22), 1),
            "delta_gmv": round(float(-user_gmv_drag), 1),
            "affected_entities": int(len(targeted_users)),
        }
        rows.append(
            {
                "date": snapshot_date,
                "snapshot_date": snapshot_date,
                "intervention_code": "soft_penalty_high_returners",
                "scenario_hash": _hash_scenario(snapshot_date, "soft_penalty_high_returners", payload),
                "before_window": "30d_before",
                "after_window": "30d_estimate",
                "observed_delta": round(payload["delta_margin"] / max(snapshot_users["gmv_last_30d"].sum(), 1), 4),
                **payload,
            }
        )

        seller_top_pct = INTERVENTION_CONFIG["dynamic_commission_high_return_sellers"]["top_pct"]
        targeted_sellers = snapshot_sellers.sort_values(
            ["return_rate_last_30d", "gmv_last_30d"], ascending=[False, False]
        ).head(max(1, round(len(snapshot_sellers) * seller_top_pct / 100)))
        commission_gain = targeted_sellers["gmv_last_30d"].sum() * (
            INTERVENTION_CONFIG["dynamic_commission_high_return_sellers"]["commission_uplift_pp"] / 100
        )
        seller_gmv_drag = targeted_sellers["gmv_last_30d"].sum() * (
            INTERVENTION_CONFIG["dynamic_commission_high_return_sellers"]["seller_gmv_drag_pct"] / 100
        )
        payload = {
            "delta_margin": round(float(commission_gain - seller_gmv_drag * 0.15), 1),
            "delta_gmv": round(float(-seller_gmv_drag), 1),
            "affected_entities": int(len(targeted_sellers)),
        }
        rows.append(
            {
                "date": snapshot_date,
                "snapshot_date": snapshot_date,
                "intervention_code": "dynamic_commission_high_return_sellers",
                "scenario_hash": _hash_scenario(snapshot_date, "dynamic_commission_high_return_sellers", payload),
                "before_window": "30d_before",
                "after_window": "30d_estimate",
                "observed_delta": round(payload["delta_margin"] / max(snapshot_sellers["gmv_last_30d"].sum(), 1), 4),
                **payload,
            }
        )

        top_products = snapshot_products.sort_values(
            ["promotion_score", "margin_contribution"], ascending=[False, False]
        ).head(max(1, round(len(snapshot_products) * INTERVENTION_CONFIG["promote_low_return_products"]["top_pct"] / 100)))
        product_gmv_uplift = (top_products["avg_price"] * top_products["orders"]).sum() * (
            INTERVENTION_CONFIG["promote_low_return_products"]["gmv_uplift_pct"] / 100
        )
        margin_ratio = (
            top_products["margin_contribution"].sum()
            / max((top_products["avg_price"] * top_products["orders"]).sum(), 1)
        )
        payload = {
            "delta_margin": round(float(product_gmv_uplift * max(margin_ratio, 0.08)), 1),
            "delta_gmv": round(float(product_gmv_uplift), 1),
            "affected_entities": int(len(top_products)),
        }
        rows.append(
            {
                "date": snapshot_date,
                "snapshot_date": snapshot_date,
                "intervention_code": "promote_low_return_products",
                "scenario_hash": _hash_scenario(snapshot_date, "promote_low_return_products", payload),
                "before_window": "30d_before",
                "after_window": "30d_estimate",
                "observed_delta": round(payload["delta_margin"] / max(snapshot_products["margin_contribution"].sum(), 1), 4),
                **payload,
            }
        )

    return pd.DataFrame(rows)


def configure_database(connection: sqlite3.Connection) -> None:
    connection.execute("pragma journal_mode = wal;")
    connection.execute("pragma synchronous = normal;")
    connection.execute("pragma foreign_keys = on;")


def create_indexes(connection: sqlite3.Connection) -> None:
    statements = [
        "create index if not exists idx_orders_fact_user_date on orders_fact (user_id, order_date);",
        "create index if not exists idx_orders_fact_seller_date on orders_fact (seller_id, order_date);",
        "create index if not exists idx_orders_fact_product_date on orders_fact (product_id, order_date);",
        "create index if not exists idx_user_agg_daily_user_date on user_agg_daily (user_id, date);",
        "create index if not exists idx_seller_agg_daily_seller_date on seller_agg_daily (seller_id, date);",
        "create index if not exists idx_product_agg_daily_product_date on product_agg_daily (product_id, date);",
        "create index if not exists idx_category_agg_daily_category_date on category_agg_daily (category_id, date);",
        "create index if not exists idx_interventions_log_target on interventions_log (target_type, target_id);",
        "create index if not exists idx_scenario_outputs_daily_code_date on scenario_outputs_daily (intervention_code, snapshot_date);",
    ]
    for statement in statements:
        connection.execute(statement)


def transform_sources(raw_data: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], PipelineRunManifest]:
    sellers = normalize_sellers(raw_data["seller_agg_daily"])
    products = normalize_products(raw_data["product_agg_daily"], sellers)
    orders = normalize_orders(raw_data["orders_fact"], raw_data["product_agg_daily"])
    synthetic_orders = build_synthetic_orders(raw_data["user_agg_daily"], raw_data["product_agg_daily"])
    orders = pd.concat([orders, synthetic_orders], ignore_index=True)
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["delivered_at"] = pd.to_datetime(orders["delivered_at"])
    orders["return_date"] = pd.to_datetime(orders["return_date"], errors="coerce")
    users = normalize_users(raw_data["user_agg_daily"], orders)
    interventions = normalize_interventions(raw_data["interventions_log"])
    categories = build_category_agg(orders, users, products)
    scenario_outputs = build_scenario_outputs(users, sellers, products)

    tables = {
        "orders_fact": orders,
        "user_agg_daily": users,
        "seller_agg_daily": sellers,
        "product_agg_daily": products,
        "category_agg_daily": categories,
        "interventions_log": interventions,
        "scenario_outputs_daily": scenario_outputs,
    }

    manifest = PipelineRunManifest(
        snapshot_date=SNAPSHOT_DATES[-1],
        source_dir=str(DEFAULT_SOURCE_DIR),
        validation_status="passed",
        record_counts={name: int(len(dataframe)) for name, dataframe in tables.items()},
        rejected_records=0,
    )
    return tables, manifest


def publish_tables(tables: dict[str, pd.DataFrame], manifest: PipelineRunManifest, db_path: Path = DB_PATH) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as connection:
        configure_database(connection)
        for table_name, dataframe in tables.items():
            dataframe.to_sql(table_name, connection, index=False, if_exists="replace")
        create_indexes(connection)

    MANIFEST_PATH.write_text(json.dumps(asdict(manifest), indent=2))
    return db_path


def run_pipeline(source_dir: Path = DEFAULT_SOURCE_DIR, db_path: Path = DB_PATH) -> PipelineRunManifest:
    adapter = CSVSnapshotAdapter(source_dir)
    raw_data = adapter.load_all()
    tables, manifest = transform_sources(raw_data)
    manifest = PipelineRunManifest(
        snapshot_date=manifest.snapshot_date,
        source_dir=str(source_dir),
        validation_status=manifest.validation_status,
        record_counts=manifest.record_counts,
        rejected_records=manifest.rejected_records,
    )
    publish_tables(tables, manifest, db_path=db_path)
    return manifest


if __name__ == "__main__":
    pipeline_manifest = run_pipeline()
    print(json.dumps(asdict(pipeline_manifest), indent=2))
