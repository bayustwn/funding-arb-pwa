"""
Account State Service
Computes MT5-grade financial metrics:
Balance, Equity, Margin, Free Margin, Margin Level %, Win Rate, and Net ROI.
"""

from typing import Optional, Dict
from datetime import datetime

from app.core.database import execute_query, execute_scalar
from app.core.config import settings
from app.schemas.state import AccountMetrics, StateResponse
from app.services.position_service import get_active_positions


async def get_system_state_map(db_path: Optional[str] = None) -> Dict[str, str]:
    """Fetches all key-value pairs from system_state table."""
    rows = await execute_query("SELECT key, value FROM system_state", db_path=db_path)
    return {r["key"]: r["value"] for r in rows}


async def get_account_metrics(db_path: Optional[str] = None) -> AccountMetrics:
    """Computes exact live MT5 financial metrics."""
    states = await get_system_state_map(db_path)
    pos_res = await get_active_positions(db_path)

    # 1. Exchange Balances
    byb_wallet = float(states.get("bybit_wallet", 0.0))
    byb_equity = float(states.get("bybit_equity", 0.0))
    bin_wallet = float(states.get("binance_wallet", 0.0))
    bin_equity = float(states.get("binance_equity", 0.0))

    balance = round(byb_wallet + bin_wallet, 4)
    if balance <= 0:
        balance = settings.TOTAL_CAPITAL_USD

    # 2. Margin & Free Margin
    margin_used = round(sum(p.margin_usd for p in pos_res.data), 4)
    free_margin = round(balance - margin_used, 4)

    # 3. Floating PnL
    floating_net = pos_res.total_floating_net_usd
    floating_market = pos_res.total_market_float_usd
    floating_fee = pos_res.total_fee_reserve_usd

    # 4. Trade Stats & Realized Profits
    tot_trades = await execute_scalar("SELECT COUNT(*) FROM completed_trades", db_path=db_path) or 0
    win_trades = await execute_scalar("SELECT COUNT(*) FROM completed_trades WHERE net_pnl_usd > 0", db_path=db_path) or 0
    loss_trades = tot_trades - win_trades
    win_rate = round((win_trades / tot_trades) * 100.0, 1) if tot_trades > 0 else 0.0

    realized_trade_pnl = await execute_scalar("SELECT SUM(net_pnl_usd) FROM completed_trades", db_path=db_path) or 0.0
    realized_trade_pnl = round(float(realized_trade_pnl), 4)

    realized_funding_pnl = await execute_scalar("SELECT SUM(income_usd) FROM funding_logs", db_path=db_path) or 0.0
    realized_funding_pnl = round(float(realized_funding_pnl), 4)

    total_realized_profit = round(realized_trade_pnl + realized_funding_pnl, 4)

    # 5. Net ROI & Liquidation Equity (Matches TUI Standard)
    # Net ROI = Total Realized Profit + Floating Net PnL of active positions
    starting_cap = settings.STARTING_CAPITAL_USD
    net_roi_usd = round(total_realized_profit + floating_net, 4)
    net_roi_pct = round((net_roi_usd / starting_cap) * 100.0, 2) if starting_cap > 0 else 0.0
    equity = round(starting_cap + net_roi_usd, 4)

    margin_level = round((equity / margin_used) * 100.0, 1) if margin_used > 0 else None

    return AccountMetrics(
        balance=balance,
        equity=equity,
        margin_used=margin_used,
        free_margin=free_margin,
        margin_level_pct=margin_level,
        starting_capital=starting_cap,
        realized_trade_pnl=realized_trade_pnl,
        realized_funding_pnl=realized_funding_pnl,
        total_realized_profit=total_realized_profit,
        floating_market_pnl=floating_market,
        floating_fee_reserve=floating_fee,
        floating_net_pnl=floating_net,
        net_roi_usd=net_roi_usd,
        net_roi_pct=net_roi_pct,
        total_trades=tot_trades,
        winning_trades=win_trades,
        losing_trades=loss_trades,
        win_rate_pct=win_rate,
        bybit_wallet=round(byb_wallet, 4),
        bybit_equity=round(byb_equity, 4),
        binance_wallet=round(bin_wallet, 4),
        binance_equity=round(bin_equity, 4),
        active_slots_used=pos_res.total_slots_used,
        max_slots=pos_res.max_slots
    )


async def get_state_response(db_path: Optional[str] = None) -> StateResponse:
    metrics = await get_account_metrics(db_path)
    return StateResponse(
        success=True,
        server_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data=metrics
    )
