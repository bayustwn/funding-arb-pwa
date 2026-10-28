"""
Market Quotes Endpoint
"""

from fastapi import APIRouter
from app.schemas.quote import QuotesResponse
from app.services.quote_service import get_market_quotes

router = APIRouter()


@router.get("", response_model=QuotesResponse, summary="Get Market Spreads & Radar Quotes")
async def get_quotes():
    """Returns scanned pairs universe, current percentage spreads, z-scores, and entry flags."""
    return await get_market_quotes()
