"""
Pydantic Schemas for Completed Trades & History (MT5 History Tab)
"""

from pydantic import BaseModel, Field
from typing import List


class CompletedTradeItem(BaseModel):
    id: int
    symbol: str
    direction: str
    direction_label: str
    entry_time: str
    exit_time: str
    hold_minutes: float
    hold_time_formatted: str
    entry_spread: float
    exit_spread: float
    notional_usd: float
    gross_pnl_usd: float
    fees_and_slip_usd: float
    net_pnl_usd: float
    exit_reason: str
    is_win: bool


class PaginatedTradesResponse(BaseModel):
    success: bool = True
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
    filter_mode: str
    total_realized_pnl_usd: float
    data: List[CompletedTradeItem]


class DailyCalendarStatItem(BaseModel):
    date: str
    total_trades: int
    win_trades: int
    loss_trades: int
    win_rate_pct: float
    total_net_pnl_usd: float


class DailySummaryResponse(BaseModel):
    success: bool = True
    days_count: int
    data: List[DailyCalendarStatItem]
