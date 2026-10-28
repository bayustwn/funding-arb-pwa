"""
Market Quotes & Radar Service
Fetches pair universe spreads and identifies arbitrage opportunities.
"""

from typing import Optional, List
from app.core.database import execute_query
from app.schemas.quote import QuoteItem, QuotesResponse


async def get_market_quotes(db_path: Optional[str] = None) -> QuotesResponse:
    """Fetches full market radar sorted by absolute spread magnitude."""
    rows = await execute_query(
        "SELECT * FROM market_spreads ORDER BY abs(spread) DESC",
        db_path=db_path
    )

    items: List[QuoteItem] = []
    ready_count = 0

    for r in rows:
        spread = float(r.get("spread", 0.0))
        z_score = float(r.get("z_score", 0.0))
        status = r.get("status", "NORMAL")
        is_ready = (abs(spread) >= 0.45 and abs(z_score) >= 2.0)

        if is_ready:
            ready_count += 1

        items.append(QuoteItem(
            symbol=r["symbol"],
            bybit_bid=float(r.get("bybit_bid", 0.0)),
            bybit_ask=float(r.get("bybit_ask", 0.0)),
            binance_bid=float(r.get("binance_bid", 0.0)),
            binance_ask=float(r.get("binance_ask", 0.0)),
            spread=round(spread, 3),
            z_score=round(z_score, 1),
            half_life=round(float(r.get("half_life", 0.0)), 1),
            status=status,
            updated_at=r.get("updated_at"),
            is_ready_opportunity=is_ready
        ))

    return QuotesResponse(
        success=True,
        total_pairs=len(items),
        ready_opportunities_count=ready_count,
        data=items
    )
