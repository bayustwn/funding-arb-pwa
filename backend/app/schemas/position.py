"""
Pydantic Schemas for Active Hedged Positions (MT5 Trade Tab)
"""

from pydantic import BaseModel, Field
from typing import List


class ActivePositionItem(BaseModel):
    id: int
    symbol: str
    direction: str
    direction_label: str = Field(..., description="Label singkat, misal 'S:BYB L:BIN' atau 'L:BYB S:BIN'")
    bybit_entry_price: float
    binance_entry_price: float
    entry_spread: float
    current_spread: float
    notional_usd: float
    margin_usd: float
    leverage: float
    entry_time: str
    hold_minutes: float
    hold_time_formatted: str
    z_score: float
    market_float_usd: float = Field(..., description="Floating PnL dari selisih pasar")
    fee_reserve_usd: float = Field(..., description="Cadangan fee taker putar balik (PP)")
    floating_net_usd: float = Field(..., description="Floating Netto Akhir")
    status: str = Field(..., description="Status posisi (PROFIT-TP, MEAN-REV, MKT-GREEN)")


class PositionsResponse(BaseModel):
    success: bool = True
    total_slots_used: int
    max_slots: int
    total_market_float_usd: float
    total_fee_reserve_usd: float
    total_floating_net_usd: float
    data: List[ActivePositionItem]
