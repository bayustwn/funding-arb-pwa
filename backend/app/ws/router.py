"""
WebSocket Endpoint for Real-time Streaming
"""

import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws.manager import manager

router = APIRouter()


@router.websocket("/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket stream for MT5 PWA client.
    Pushes tick updates at configured interval.
    Responds to client ping messages with immediate pong heartbeat.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Listen for client heartbeat/pings
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
                if msg.get("event") == "ping":
                    await websocket.send_text(json.dumps({
                        "event": "pong",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }))
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
