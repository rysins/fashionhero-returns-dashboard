from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class UserThresholds:
    toxic_return_rate: float = 0.55
    toxic_margin_per_order: float = 0.0
    high_value_gmv: float = 900.0
    high_value_return_rate: float = 0.20
    high_value_margin_per_order: float = 25.0
    tryer_orders_max: int = 2
    tryer_return_rate: float = 0.25


@dataclass(frozen=True)
class SellerThresholds:
    risky_return_rate: float = 0.50
    warning_return_rate: float = 0.35
    risky_margin_contribution: float = 0.0
    warning_margin_contribution: float = 75.0


USER_THRESHOLDS = UserThresholds()
SELLER_THRESHOLDS = SellerThresholds()


def margin_health_badge(contribution_per_order: float) -> str:
    if contribution_per_order >= 18:
        return "healthy"
    if contribution_per_order >= 8:
        return "warning"
    return "critical"


def return_rate_badge(return_rate: float) -> str:
    if return_rate <= 0.30:
        return "healthy"
    if return_rate <= 0.40:
        return "warning"
    return "critical"


def toxic_order_share_badge(share: float) -> str:
    if share <= 0.12:
        return "healthy"
    if share <= 0.20:
        return "warning"
    return "critical"
