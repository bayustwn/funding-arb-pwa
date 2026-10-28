"""
Pydantic Schemas for Funding Fee Logs (MT5 Swap Details)
"""

from pydantic import BaseModel
from typing import List


class FundingLogItem(BaseModel):
    id: int
    exchange: str
    symbol: str
    income_usd: float
    timestamp: str
    created_at: str


class FundingSummary(BaseModel):
    binance_gross_usd: float
    bybit_gross_usd: float
    net_funding_usd: float
    total_logs_count: int


class PaginatedFundingResponse(BaseModel):
    success: bool = True
    summary: FundingSummary
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    data: List[FundingLogItem]
