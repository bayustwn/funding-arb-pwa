"""
Pytest Fixtures for FastAPI Gateway Tests
Sets up an isolated SQLite test database with realistic mock data matching the trading engine.
"""

import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("db")
    db_file = str(temp_dir / "test_arbitrage.db")

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # 1. active_positions
    cur.execute("""
    CREATE TABLE active_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE NOT NULL,
        direction TEXT NOT NULL,
        bybit_entry_price REAL NOT NULL,
        binance_entry_price REAL NOT NULL,
        notional_usd REAL NOT NULL,
        margin_usd REAL NOT NULL,
        leverage REAL NOT NULL,
        entry_spread REAL NOT NULL,
        current_spread REAL NOT NULL,
        entry_time TEXT NOT NULL,
        hold_minutes REAL DEFAULT 0.0,
        z_score REAL DEFAULT 0.0,
        floating_net_usd REAL DEFAULT 0.0,
        bybit_order_id TEXT,
        binance_order_id TEXT
    );
    """)

    # 2. completed_trades
    cur.execute("""
    CREATE TABLE completed_trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        direction TEXT NOT NULL,
        entry_time TEXT NOT NULL,
        exit_time TEXT NOT NULL,
        hold_minutes REAL NOT NULL,
        entry_spread REAL NOT NULL,
        exit_spread REAL NOT NULL,
        bybit_entry_price REAL,
        binance_entry_price REAL,
        bybit_exit_price REAL,
        binance_exit_price REAL,
        qty REAL,
        notional_usd REAL NOT NULL,
        margin_used_usd REAL,
        leverage REAL,
        gross_pnl_usd REAL NOT NULL,
        fees_and_slip_usd REAL NOT NULL,
        net_pnl_usd REAL NOT NULL,
        exit_reason TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        funding_collected_usd REAL DEFAULT 0.0
    );
    """)

    # 3. market_spreads
    cur.execute("""
    CREATE TABLE market_spreads (
        symbol TEXT PRIMARY KEY,
        bybit_bid REAL NOT NULL,
        bybit_ask REAL NOT NULL,
        binance_bid REAL NOT NULL,
        binance_ask REAL NOT NULL,
        spread REAL NOT NULL,
        z_score REAL NOT NULL,
        half_life REAL NOT NULL,
        status TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 4. system_state
    cur.execute("""
    CREATE TABLE system_state (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. funding_logs
    cur.execute("""
    CREATE TABLE funding_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exchange TEXT NOT NULL,
        symbol TEXT NOT NULL,
        income_usd REAL NOT NULL,
        timestamp TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. symbol_fee_cache
    cur.execute("""
    CREATE TABLE symbol_fee_cache (
        symbol TEXT PRIMARY KEY,
        bybit_taker REAL NOT NULL,
        bybit_maker REAL NOT NULL,
        binance_taker REAL NOT NULL,
        binance_maker REAL NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Insert Sample Data
    cur.execute("""
    INSERT INTO system_state (key, value) VALUES
    ('bybit_wallet', '14.8147'),
    ('bybit_equity', '14.8325'),
    ('binance_wallet', '15.0878'),
    ('binance_equity', '15.0466');
    """)

    cur.execute("""
    INSERT INTO active_positions (symbol, direction, bybit_entry_price, binance_entry_price, notional_usd, margin_usd, leverage, entry_spread, current_spread, entry_time, hold_minutes, z_score, floating_net_usd)
    VALUES
    ('IOSTUSDT', 'SHORT_BYBIT_LONG_BINANCE', 0.0055, 0.0054, 12.0, 6.0, 2.0, 0.82, 0.50, '2026-10-28 07:51:06', 35.0, 0.9, 0.0016),
    ('BMTUSDT', 'SHORT_BYBIT_LONG_BINANCE', 0.1250, 0.1240, 12.0, 6.0, 2.0, 0.63, 0.76, '2026-10-28 06:01:27', 145.0, -0.1, -0.0315);
    """)

    cur.execute("""
    INSERT INTO completed_trades (symbol, direction, entry_time, exit_time, hold_minutes, entry_spread, exit_spread, notional_usd, gross_pnl_usd, fees_and_slip_usd, net_pnl_usd, exit_reason)
    VALUES
    ('IRYSUSDT', 'SHORT_BYBIT_LONG_BINANCE', '2026-10-28 06:31:32', '2026-10-28 08:07:22', 95.8, 0.65, 0.28, 12.0, 0.0330, 0.0240, 0.0090, 'TP_REVERSION_65%'),
    ('DOODUSDT', 'SHORT_BYBIT_LONG_BINANCE', '2026-10-28 07:38:42', '2026-10-28 07:50:08', 11.4, 1.09, 0.23, 12.0, 0.0496, 0.0240, 0.0256, 'TP_NET_TARGET');
    """)

    cur.execute("""
    INSERT INTO market_spreads (symbol, bybit_bid, bybit_ask, binance_bid, binance_ask, spread, z_score, half_life, status, updated_at)
    VALUES
    ('ORDERUSDT', 0.1550, 0.1551, 0.1540, 0.1541, 0.65, 2.3, 12.0, 'READY', '2026-10-28 08:20:00'),
    ('BTCUSDT', 68000.0, 68001.0, 68000.5, 68001.5, 0.01, 0.2, 5.0, 'NORMAL', '2026-10-28 08:20:00');
    """)

    cur.execute("""
    INSERT INTO funding_logs (exchange, symbol, income_usd, timestamp)
    VALUES
    ('BYBIT', 'IRYSUSDT', -0.0150, '1729000000'),
    ('BINANCE', 'IRYSUSDT', 0.0020, '1729000000');
    """)

    conn.commit()
    conn.close()

    # Override settings for tests
    settings.DB_PATH = db_file
    return db_file


@pytest.fixture
def client(test_db_path):
    with TestClient(app) as test_client:
        yield test_client
