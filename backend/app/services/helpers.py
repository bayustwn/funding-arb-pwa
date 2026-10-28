"""
Shared Business Helpers & Formatting Utilities
"""

import math
from typing import Optional


def format_hold_time(minutes: Optional[float]) -> str:
    """Formats hold time in minutes to 'Xj YYm' (e.g. 1j 49m, 0j 18m)."""
    if minutes is None:
        return "-"
    tot = int(round(minutes))
    h = tot // 60
    m = tot % 60
    return f"{h}j {m:02d}m"


def get_direction_label(direction: str) -> str:
    """Maps internal direction to MT5 style short label."""
    if direction == "SHORT_BYBIT_LONG_BINANCE":
        return "S:BYB L:BIN"
    elif direction == "LONG_BYBIT_SHORT_BINANCE":
        return "L:BYB S:BIN"
    return direction


def calculate_dynamic_fee_reserve(notional_per_leg: float, byb_taker_rate: float = 0.00055, bin_taker_rate: float = 0.00050) -> float:
    """
    Computes exact round-trip taker fees + slippage reserve:
    Round-trip fees for 2 legs = 2 * (byb_rate + bin_rate + 2*slippage) * notional_per_leg
    """
    slip_rate = 0.0002  # 0.02%
    byb_cost = 2 * byb_taker_rate * notional_per_leg
    bin_cost = 2 * bin_taker_rate * notional_per_leg
    slip_cost = 4 * slip_rate * notional_per_leg
    return round(byb_cost + bin_cost + slip_cost, 4)
