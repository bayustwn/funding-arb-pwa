"""
Active Positions Service
Fetches active hedged positions and computes exact floating PnL and fee reserves.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import execute_query
from app.core.config import settings
from app.schemas.position import ActivePositionItem, PositionsResponse
from app.services.helpers import format_hold_time, get_direction_label, calculate_dynamic_fee_reserve


async def get_symbol_fee_cache(db_path: Optional[str] = None) -> Dict[str, Dict[str, float]]:
    """Loads fee cache for accurate per-symbol fee calculation."""
    rows = await execute_query("SELECT symbol, bybit_taker, binance_taker FROM symbol_fee_cache", db_path=db_path)
    res = {}
    for r in rows:
        res[r["symbol"]] = {
            "bybit_taker": float(r["bybit_taker"]),
            "binance_taker": float(r["binance_taker"])
        }
    return res


async def get_active_positions(db_path: Optional[str] = None) -> PositionsResponse:
    """
    Returns full active positions list with MT5 metrics:
    - Market Gross Float
    - Fee Reserve PP
    - Net Float
    - Status flags
    """
    rows = await execute_query("SELECT * FROM active_positions ORDER BY id ASC", db_path=db_path)
    fee_cache = await get_symbol_fee_cache(db_path)

    items: List[ActivePositionItem] = []
    tot_market_float = 0.0
    tot_fee_reserve = 0.0
    tot_net_float = 0.0

    now = datetime.now()

    for r in rows:
        sym = r["symbol"]
        direction = r["direction"]
        notional_usd = float(r.get("notional_usd", 12.0))
        notional_leg = notional_usd / 2.0
        margin_usd = float(r.get("margin_usd", 6.0))
        leverage = float(r.get("leverage", settings.LEVERAGE))
        byb_entry = float(r["bybit_entry_price"])
        bin_entry = float(r["binance_entry_price"])
        entry_spread = float(r["entry_spread"])
        cur_spread = float(r["current_spread"])
        z_score = float(r.get("z_score", 0.0))
        stored_net_float = float(r.get("floating_net_usd", 0.0))

        # Dynamic fee reserve for this pair
        sym_fees = fee_cache.get(sym, {"bybit_taker": 0.00055, "binance_taker": 0.00050})
        fee_reserve = calculate_dynamic_fee_reserve(
            notional_leg,
            byb_taker_rate=sym_fees["bybit_taker"],
            bin_taker_rate=sym_fees["binance_taker"]
        )

        # Calculate hold minutes
        entry_time_str = r.get("entry_time", "")
        hold_min = float(r.get("hold_minutes", 0.0))
        if entry_time_str:
            try:
                dt_entry = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
                hold_min = max(hold_min, (now - dt_entry).total_seconds() / 60.0)
            except Exception:
                pass

        # Market Gross Float = stored_net_float + fee_reserve
        market_float = round(stored_net_float + fee_reserve, 4)
        net_float = stored_net_float

        tot_market_float += market_float
        tot_fee_reserve += fee_reserve
        tot_net_float += net_float

        # Determine MT5-style status badge
        if net_float > 0.0005:
            status = "PROFIT-TP"
        elif market_float > 0.0005:
            status = "MKT-GREEN"
        else:
            status = "MEAN-REV"

        items.append(ActivePositionItem(
            id=r["id"],
            symbol=sym,
            direction=direction,
            direction_label=get_direction_label(direction),
            bybit_entry_price=byb_entry,
            binance_entry_price=bin_entry,
            entry_spread=entry_spread,
            current_spread=cur_spread,
            notional_usd=notional_usd,
            margin_usd=margin_usd,
            leverage=leverage,
            entry_time=entry_time_str,
            hold_minutes=round(hold_min, 1),
            hold_time_formatted=format_hold_time(hold_min),
            z_score=round(z_score, 1),
            market_float_usd=round(market_float, 4),
            fee_reserve_usd=round(-fee_reserve, 4),
            floating_net_usd=round(net_float, 4),
            status=status
        ))

    return PositionsResponse(
        success=True,
        total_slots_used=len(items),
        max_slots=settings.MAX_CONCURRENT_SLOTS,
        total_market_float_usd=round(tot_market_float, 4),
        total_fee_reserve_usd=round(-tot_fee_reserve, 4),
        total_floating_net_usd=round(tot_net_float, 4),
        data=items
    )
