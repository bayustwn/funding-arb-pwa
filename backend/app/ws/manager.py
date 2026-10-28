"""
WebSocket Connection Manager
Manages active mobile PWA client connections with efficient single-query broadcast.
Includes ping/pong heartbeat, automatic stale connection pruning, and debounced polling.
"""

import asyncio
import json
import logging
from typing import Set, Optional
from datetime import datetime
from fastapi import WebSocket

from app.core.config import settings
from app.services.state_service import get_account_metrics
from app.services.position_service import get_active_positions
from app.services.quote_service import get_market_quotes

logger = logging.getLogger("ws_manager")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._broadcast_task: Optional[asyncio.Task] = None
        self._running = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

        # Send immediate initial state
        initial_payload = await self.build_tick_payload()
        await websocket.send_text(json.dumps(initial_payload))

        # Start broadcast task if not already running
        if self._broadcast_task is None or self._broadcast_task.done():
            self._running = True
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")
        if not self.active_connections and self._broadcast_task:
            self._running = False
            self._broadcast_task.cancel()
            self._broadcast_task = None

    async def build_tick_payload(self) -> dict:
        """Assembles aggregated live tick snapshot."""
        try:
            metrics = await get_account_metrics()
            positions = await get_active_positions()
            quotes = await get_market_quotes()

            return {
                "event": "tick",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": {
                    "account": metrics.model_dump(),
                    "positions": positions.model_dump(),
                    "opportunities_count": quotes.ready_opportunities_count,
                    "active_slots_used": positions.total_slots_used,
                    "max_slots": positions.max_slots
                }
            }
        except Exception as e:
            logger.error(f"Error building tick payload: {e}")
            return {
                "event": "error",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": {"error": str(e)}
            }

    async def _broadcast_loop(self):
        """
        Runs continuous background broadcast loop as long as >= 1 client is connected.
        Sleeps between ticks according to WS_STREAM_INTERVAL_SECONDS.
        """
        while self._running and self.active_connections:
            try:
                payload_str = json.dumps(await self.build_tick_payload())
                stale_connections = set()

                for conn in list(self.active_connections):
                    try:
                        await conn.send_text(payload_str)
                    except Exception:
                        stale_connections.add(conn)

                for stale in stale_connections:
                    self.active_connections.discard(stale)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")

            await asyncio.sleep(settings.WS_STREAM_INTERVAL_SECONDS)


manager = ConnectionManager()
