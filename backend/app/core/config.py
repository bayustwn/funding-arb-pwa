"""
Core Application Configuration
Centralized settings loaded from environment variables with safe defaults.
Zero external dependency on pydantic-settings to maintain maximum compatibility.
"""

import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # App Information
    APP_NAME: str = "Funding Arbitrage MT5 Gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")

    # Server Bindings
    HOST: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))

    # Database
    # Defaults to STB path if exists, otherwise local fallback
    DB_PATH: str = Field(
        default_factory=lambda: os.getenv(
            "DB_PATH",
            "/root/funding-arb/data/arbitrage.db"
            if os.path.exists("/root/funding-arb/data/arbitrage.db")
            else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "funding-arb", "data", "arbitrage.db")
        )
    )

    # CORS Origins (Allow local network, Tailscale, localhost, and PWA origin)
    CORS_ORIGINS: List[str] = [
        "*",  # Open for internal LAN / Tailscale
    ]

    # WebSocket Stream Interval
    WS_STREAM_INTERVAL_SECONDS: float = Field(
        default_factory=lambda: float(os.getenv("WS_STREAM_INTERVAL_SECONDS", "1.5"))
    )

    # Trading Reference Parameters (Synced with Bot Config)
    STARTING_CAPITAL_USD: float = Field(
        default_factory=lambda: float(os.getenv("STARTING_CAPITAL_USD", "29.8778"))
    )
    TOTAL_CAPITAL_USD: float = Field(
        default_factory=lambda: float(os.getenv("TOTAL_CAPITAL_USD", "30.00"))
    )
    MAX_CONCURRENT_SLOTS: int = Field(
        default_factory=lambda: int(os.getenv("MAX_CONCURRENT_SLOTS", "3"))
    )
    LEVERAGE: float = Field(
        default_factory=lambda: float(os.getenv("LEVERAGE", "2.0"))
    )


settings = Settings()
