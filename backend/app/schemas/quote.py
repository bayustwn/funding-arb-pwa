"""
Pydantic Schemas for Market Radar Quotes (MT5 Quotes Tab)
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class QuoteItem(BaseModel):
    symbol: str
    bybit_bid: float
    bybit_ask: float
    binance_bid: float
    binance_ask: float
    spread: float = Field(..., description="Percentage spread: (Bybit - Binance) / Binance * 100")
    z_score: float
    half_life: float
    status: str
    updated_at: Optional[str] = None
    is_ready_opportunity: bool = False


class QuotesResponse(BaseModel):
    success: bool = True
    total_pairs: int
    ready_opportunities_count: int
    data: List[QuoteItem]
