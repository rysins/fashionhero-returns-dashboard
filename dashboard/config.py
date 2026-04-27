from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
PHASE2_CONFIG_PATH = ROOT_DIR / "shared" / "fashionhero_phase2_config.json"

USER_SEGMENT_ORDER = ["high_value", "toxic", "tryers", "low_value"]
SELLER_SEGMENT_ORDER = ["healthy", "warning", "risky"]

USER_SEGMENT_COLORS = {
    "high_value": "#2f7d4a",
    "toxic": "#9e4040",
    "tryers": "#c9862b",
    "low_value": "#56708a",
}

SELLER_SEGMENT_COLORS = {
    "healthy": "#2f7d4a",
    "warning": "#c9862b",
    "risky": "#9e4040",
}

CATEGORY_HEALTH_COLORS = {
    "healthy": "#2f7d4a",
    "warning": "#c9862b",
    "critical": "#9e4040",
}


@dataclass(frozen=True)
class UserThresholds:
    toxic_return_rate: float
    toxic_margin_per_order: float
    high_value_gmv: float
    high_value_return_rate: float
    high_value_margin_per_order: float
    tryer_orders_max: int
    tryer_return_rate: float


@dataclass(frozen=True)
class SellerThresholds:
    risky_return_rate: float
    warning_return_rate: float
    risky_margin_contribution: float
    warning_margin_contribution: float


@dataclass(frozen=True)
class CategoryThresholds:
    healthy_return_rate_max: float
    warning_return_rate_max: float
    healthy_margin_per_order_min: float
    warning_margin_per_order_min: float


def load_phase2_config() -> dict:
    with PHASE2_CONFIG_PATH.open() as handle:
        return json.load(handle)


PHASE2_CONFIG = load_phase2_config()
USER_THRESHOLDS = UserThresholds(**PHASE2_CONFIG["user_thresholds"])
SELLER_THRESHOLDS = SellerThresholds(**PHASE2_CONFIG["seller_thresholds"])
CATEGORY_THRESHOLDS = CategoryThresholds(**PHASE2_CONFIG["category_thresholds"])
INTERVENTION_CONFIG = PHASE2_CONFIG["interventions"]


def margin_health_badge(contribution_per_order: float) -> str:
    if contribution_per_order >= CATEGORY_THRESHOLDS.healthy_margin_per_order_min:
        return "healthy"
    if contribution_per_order >= CATEGORY_THRESHOLDS.warning_margin_per_order_min:
        return "warning"
    return "critical"


def return_rate_badge(return_rate: float) -> str:
    if return_rate <= CATEGORY_THRESHOLDS.healthy_return_rate_max:
        return "healthy"
    if return_rate <= CATEGORY_THRESHOLDS.warning_return_rate_max:
        return "warning"
    return "critical"


def toxic_order_share_badge(share: float) -> str:
    if share <= 0.12:
        return "healthy"
    if share <= 0.20:
        return "warning"
    return "critical"


def category_health_badge(return_rate: float, contribution_per_order: float) -> str:
    return_score = return_rate_badge(return_rate)
    margin_score = margin_health_badge(contribution_per_order)
    if "critical" in {return_score, margin_score}:
        return "critical"
    if "warning" in {return_score, margin_score}:
        return "warning"
    return "healthy"
