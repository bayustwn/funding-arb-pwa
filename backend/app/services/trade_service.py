"""
Completed Trades & History Service
Supports paginated trades retrieval, win/loss filtering, and calendar summaries.
"""

import math
from typing import Optional, List
from app.core.database import execute_query, execute_scalar
from app.schemas.trade import (
    CompletedTradeItem,
    PaginatedTradesResponse,
    DailyCalendarStatItem,
    DailySummaryResponse
)
from app.services.helpers import format_hold_time, get_direction_label


async def get_completed_trades_paginated(
    page: int = 1,
    page_size: int = 15,
    filter_mode: str = "ALL",
    db_path: Optional[str] = None
) -> PaginatedTradesResponse:
    """Fetches paginated trades with filtering."""
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    offset = (page - 1) * page_size

    where_clause = ""
    if filter_mode.upper() == "WIN":
        where_clause = "WHERE net_pnl_usd > 0"
    elif filter_mode.upper() == "LOSS":
        where_clause = "WHERE net_pnl_usd <= 0"

    count_query = f"SELECT COUNT(*) FROM completed_trades {where_clause}"
    total_items = await execute_scalar(count_query, db_path=db_path) or 0
    total_pages = max(1, math.ceil(total_items / page_size))

    tot_pnl_query = f"SELECT SUM(net_pnl_usd) FROM completed_trades {where_clause}"
    tot_pnl = await execute_scalar(tot_pnl_query, db_path=db_path) or 0.0

    data_query = f"""
    SELECT * FROM completed_trades
    {where_clause}
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """
    rows = await execute_query(data_query, (page_size, offset), db_path=db_path)

    items: List[CompletedTradeItem] = []
    for r in rows:
        net_pnl = float(r.get("net_pnl_usd", 0.0))
        hold_min = float(r.get("hold_minutes", 0.0))
        dir_str = r.get("direction", "")

        items.append(CompletedTradeItem(
            id=r["id"],
            symbol=r["symbol"],
            direction=dir_str,
            direction_label=get_direction_label(dir_str),
            entry_time=r.get("entry_time", ""),
            exit_time=r.get("exit_time", ""),
            hold_minutes=round(hold_min, 1),
            hold_time_formatted=format_hold_time(hold_min),
            entry_spread=round(float(r.get("entry_spread", 0.0)), 3),
            exit_spread=round(float(r.get("exit_spread", 0.0)), 3),
            notional_usd=round(float(r.get("notional_usd", 12.0)), 2),
            gross_pnl_usd=round(float(r.get("gross_pnl_usd", 0.0)), 4),
            fees_and_slip_usd=round(float(r.get("fees_and_slip_usd", 0.0)), 4),
            net_pnl_usd=round(net_pnl, 4),
            exit_reason=r.get("exit_reason", ""),
            is_win=(net_pnl > 0)
        ))

    return PaginatedTradesResponse(
        success=True,
        total_items=total_items,
        total_pages=total_pages,
        current_page=page,
        page_size=page_size,
        filter_mode=filter_mode.upper(),
        total_realized_pnl_usd=round(float(tot_pnl), 4),
        data=items
    )


async def get_daily_calendar_summary(db_path: Optional[str] = None) -> DailySummaryResponse:
    """Summarizes trades by calendar date (YYYY-MM-DD)."""
    query = """
    SELECT
        date(exit_time) as trade_date,
        COUNT(*) as total_trades,
        SUM(CASE WHEN net_pnl_usd > 0 THEN 1 ELSE 0 END) as win_trades,
        SUM(CASE WHEN net_pnl_usd <= 0 THEN 1 ELSE 0 END) as loss_trades,
        SUM(net_pnl_usd) as total_net_pnl
    FROM completed_trades
    GROUP BY date(exit_time)
    ORDER BY trade_date DESC
    """
    rows = await execute_query(query, db_path=db_path)

    items: List[DailyCalendarStatItem] = []
    for r in rows:
        tot = r["total_trades"]
        win = r["win_trades"] or 0
        loss = r["loss_trades"] or 0
        pnl = r["total_net_pnl"] or 0.0
        win_rate = round((win / tot) * 100.0, 1) if tot > 0 else 0.0

        items.append(DailyCalendarStatItem(
            date=r["trade_date"] or "Unknown",
            total_trades=tot,
            win_trades=win,
            loss_trades=loss,
            win_rate_pct=win_rate,
            total_net_pnl_usd=round(float(pnl), 4)
        ))

    return DailySummaryResponse(
        success=True,
        days_count=len(items),
        data=items
    )
