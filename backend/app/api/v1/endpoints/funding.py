"""
Funding Fee Logs Endpoint
"""

from fastapi import APIRouter, Query
from app.schemas.funding import PaginatedFundingResponse
from app.services.funding_service import get_funding_logs_paginated

router = APIRouter()


@router.get("", response_model=PaginatedFundingResponse, summary="Get Funding Rate Logs")
async def get_funding(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Returns historical funding settlements per exchange with net funding summary."""
    return await get_funding_logs_paginated(page=page, page_size=page_size)
