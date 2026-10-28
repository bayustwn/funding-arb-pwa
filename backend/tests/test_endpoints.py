"""
Unit Tests for REST API Endpoints
"""

import pytest


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert data["max_slots"] == 3


def test_get_state(client):
    res = client.get("/api/v1/state")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    d = body["data"]

    # Verify MT5 Metrics
    # Bybit wallet 14.8147 + Binance wallet 15.0878 = 29.9025
    assert d["balance"] == 29.9025
    # 2 active positions * $6 = $12 margin
    assert d["margin_used"] == 12.0
    assert d["free_margin"] == 17.9025
    assert d["active_slots_used"] == 2
    assert d["max_slots"] == 3
    assert d["total_trades"] == 2
    assert d["winning_trades"] == 2
    assert d["win_rate_pct"] == 100.0


def test_get_positions(client):
    res = client.get("/api/v1/positions")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["total_slots_used"] == 2
    assert len(body["data"]) == 2

    # Check first position (IOSTUSDT)
    p0 = body["data"][0]
    assert p0["symbol"] == "IOSTUSDT"
    assert p0["direction_label"] == "S:BYB L:BIN"
    assert p0["notional_usd"] == 12.0
    assert p0["margin_usd"] == 6.0
    assert p0["status"] == "PROFIT-TP"


def test_get_trades_paginated(client):
    res = client.get("/api/v1/trades?page=1&page_size=10&filter_mode=ALL")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["total_items"] == 2
    assert body["total_pages"] == 1
    assert len(body["data"]) == 2

    # Test filtering
    res_win = client.get("/api/v1/trades?filter_mode=WIN")
    assert res_win.status_code == 200
    assert res_win.json()["total_items"] == 2

    res_loss = client.get("/api/v1/trades?filter_mode=LOSS")
    assert res_loss.status_code == 200
    assert res_loss.json()["total_items"] == 0


def test_get_daily_trades(client):
    res = client.get("/api/v1/trades/daily")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["days_count"] >= 1
    assert body["data"][0]["total_trades"] == 2
    assert body["data"][0]["win_rate_pct"] == 100.0


def test_get_quotes(client):
    res = client.get("/api/v1/quotes")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["total_pairs"] == 2
    assert body["ready_opportunities_count"] == 1

    # First pair ORDERUSDT should be flagged ready
    q0 = body["data"][0]
    assert q0["symbol"] == "ORDERUSDT"
    assert q0["is_ready_opportunity"] is True


def test_get_funding(client):
    res = client.get("/api/v1/funding?page=1&page_size=10")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["total_items"] == 2
    summary = body["summary"]
    # Bybit -0.0150, Binance +0.0020 -> Net: -0.0130
    assert pytest.approx(summary["net_funding_usd"], 0.0001) == -0.0130
