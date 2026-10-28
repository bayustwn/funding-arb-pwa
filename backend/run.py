#!/usr/bin/env python3
"""
CLI runner for Funding Arbitrage Gateway
Usage:
    python run.py [--port 8000] [--host 0.0.0.0]
"""

import sys
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1,
        log_level="info"
    )
