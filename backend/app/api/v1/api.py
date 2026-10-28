"""
API v1 Router Aggregator
Combines all domain endpoints into a unified router.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import state, positions, trades, quotes, funding

api_router = APIRouter()

api_router.include_router(state.router, prefix="/state", tags=["Account State"])
api_router.include_router(positions.router, prefix="/positions", tags=["Active Positions"])
api_router.include_router(trades.router, prefix="/trades", tags=["Trades History"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["Market Quotes"])
api_router.include_router(funding.router, prefix="/funding", tags=["Funding Logs"])
