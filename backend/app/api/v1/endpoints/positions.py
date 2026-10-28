"""
Active Positions Endpoint
"""

from fastapi import APIRouter
from app.schemas.position import PositionsResponse
from app.services.position_service import get_active_positions

router = APIRouter()


@router.get("", response_model=PositionsResponse, summary="Get Active Hedged Positions")
async def get_positions():
    """
    Returns active hedged slots with live market floating, fee reserves, hold duration, and status.
    """
    return await get_active_positions()
