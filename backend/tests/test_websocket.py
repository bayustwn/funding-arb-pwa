"""
Unit Tests for WebSocket Real-time Stream
"""

import json
import pytest


def test_websocket_stream_initial_tick_and_ping(client):
    with client.websocket_connect("/ws/stream") as websocket:
        # 1. First frame sent upon connect is initial tick
        raw_msg = websocket.receive_text()
        msg = json.loads(raw_msg)
        assert msg["event"] == "tick"
        assert "data" in msg
        assert "account" in msg["data"]
        assert "positions" in msg["data"]
        assert msg["data"]["account"]["balance"] == 29.9025
        assert msg["data"]["active_slots_used"] == 2

        # 2. Test ping/pong heartbeat
        websocket.send_text(json.dumps({"event": "ping"}))
        pong_raw = websocket.receive_text()
        pong = json.loads(pong_raw)
        assert pong["event"] == "pong"
