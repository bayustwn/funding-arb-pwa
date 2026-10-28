"""
Pydantic Schemas for WebSocket Stream Messages
"""

from pydantic import BaseModel
from typing import Any, Optional


class WsMessage(BaseModel):
    event: str  # "tick", "ping", "pong", "error", "connected"
    timestamp: str
    data: Optional[Any] = None
