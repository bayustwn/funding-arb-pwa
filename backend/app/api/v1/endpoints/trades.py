"""
Trades & History Endpoints
"""

from fastapi import APIRouter, Query
from app.schemas.trade import PaginatedTradesResponse, DailySummaryResponse
from app.services.trade_service import (
    get_completed_trades_paginated,
    get_daily_calendar_summary
)

router = APIRouter()


@router.get("", response_model=PaginatedTradesResponse, summary="Get Paginated Completed Trades")
async def get_trades(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(15, ge=1, le=100, description="Items per page"),
    filter_mode: str = Query("ALL", pattern="^(ALL|WIN|LOSS)$", description="Filter by ALL, WIN, or LOSS")
):
    """Returns completed trade history with net PnL, hold time, and execution triggers."""
    return await get_completed_trades_paginated(page=page, page_size=page_size, filter_mode=filter_mode)


@router.get("/daily", response_model=DailySummaryResponse, summary="Get Daily Calendar Performance Summary")
async def get_daily_trades():
    """Returns aggregated daily performance, trade counts, win rate, and net PnL."""
    return await get_daily_calendar_summary()
