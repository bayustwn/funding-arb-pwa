"""
FastAPI Application Entry Point & Gateway Engine
Industry-grade setup:
- Async lifespan lifecycle management
- CORS middleware with open LAN/Tailscale policy
- GZip compression for mobile network efficiency
- Healthcheck & System info
- Modular API v1 router and WebSocket streaming
- Static file serving support for PWA build
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.ws.router import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    print(f"================================================================================")
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} INITIALIZING")
    print(f"Database: {settings.DB_PATH}")
    print(f"Slots Config: {settings.MAX_CONCURRENT_SLOTS} | Leverage: {settings.LEVERAGE}x")
    print(f"================================================================================")
    yield
    print(f"🛑 {settings.APP_NAME} SHUTTING DOWN")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="High-performance read-only gateway for MT5-style Funding Arbitrage PWA monitor.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. CORS Middleware (Essential for PWA across local IP / Tailscale)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. GZip Compression Middleware (High efficiency over mobile networks)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. Mount API v1 & WebSocket Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/ws", tags=["WebSocket Stream"])


# 4. Root & Health Check Endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Service health and database accessibility check."""
    db_exists = os.path.exists(settings.DB_PATH)
    return {
        "status": "healthy" if db_exists else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database_connected": db_exists,
        "max_slots": settings.MAX_CONCURRENT_SLOTS
    }


# 5. Static Files for PWA Frontend (If frontend build exists in dist/)
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/", tags=["Info"])
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "docs": "/docs",
            "health": "/health",
            "api_v1": "/api/v1",
            "websocket_stream": "/ws/stream"
        }
