"""
Funding Fee Logs Service
Summarizes historical funding income/deductions per exchange.
"""

import math
from typing import Optional, List
from app.core.database import execute_query, execute_scalar
from app.schemas.funding import (
    FundingLogItem,
    FundingSummary,
    PaginatedFundingResponse
)


async def get_funding_logs_paginated(
    page: int = 1,
    page_size: int = 20,
    db_path: Optional[str] = None
) -> PaginatedFundingResponse:
    """Fetches funding transaction logs paginated."""
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    offset = (page - 1) * page_size

    total_items = await execute_scalar("SELECT COUNT(*) FROM funding_logs", db_path=db_path) or 0
    total_pages = max(1, math.ceil(total_items / page_size))

    # Calculate summaries
    bin_sum = await execute_scalar(
        "SELECT SUM(income_usd) FROM funding_logs WHERE exchange = 'BINANCE'",
        db_path=db_path
    ) or 0.0
    byb_sum = await execute_scalar(
        "SELECT SUM(income_usd) FROM funding_logs WHERE exchange = 'BYBIT'",
        db_path=db_path
    ) or 0.0
    net_funding = bin_sum + byb_sum

    rows = await execute_query(
        "SELECT * FROM funding_logs ORDER BY id DESC LIMIT ? OFFSET ?",
        (page_size, offset),
        db_path=db_path
    )

    items: List[FundingLogItem] = []
    for r in rows:
        items.append(FundingLogItem(
            id=r["id"],
            exchange=r["exchange"],
            symbol=r["symbol"],
            income_usd=round(float(r["income_usd"]), 6),
            timestamp=str(r["timestamp"]),
            created_at=str(r.get("created_at", ""))
        ))

    return PaginatedFundingResponse(
        success=True,
        summary=FundingSummary(
            binance_gross_usd=round(float(bin_sum), 4),
            bybit_gross_usd=round(float(byb_sum), 4),
            net_funding_usd=round(float(net_funding), 4),
            total_logs_count=total_items
        ),
        current_page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        data=items
    )
