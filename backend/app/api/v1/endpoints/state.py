"""
Account & System State Endpoint
"""

from fastapi import APIRouter
from app.schemas.state import StateResponse
from app.services.state_service import get_state_response

router = APIRouter()


@router.get("", response_model=StateResponse, summary="Get MT5 Account Financial State")
async def get_state():
    """
    Returns full live financial metrics:
    Balance, Equity, Margin, Free Margin, Margin Level %, Realized PnL, Floating PnL, and Win Rate.
    """
    return await get_state_response()
