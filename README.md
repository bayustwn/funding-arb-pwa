# 📱 Funding Arbitrage MT5 Gateway (PWA Backend)

High-performance, read-only REST & WebSocket gateway designed for mobile Progressive Web Apps (PWA) monitoring the **Binance - Bybit Funding Arbitrage Bot**.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph STB ["STB Host (Armbian Linux)"]
        BOT["Trading Daemon (funding-arb.service)"] -->|Writes| DB[("arbitrage.db (WAL Mode)")]
        API["FastAPI Gateway (funding-api.service)"] -->|Read-Only Async| DB
    end

    subgraph CLIENTS ["Clients (Mobile / Desktop)"]
        PWA["MT5 Android PWA (Browser / Standalone)"]
    end

    API -->|REST API /api/v1| PWA
    API <-->|WebSocket Stream /ws/stream (1.5s)| PWA
```

- **Zero Trading Lock Contention**: SQLite queries execute with `PRAGMA query_only = ON` in dedicated asyncio worker threads.
- **Debounced Broadcasting**: A single server loop polls SQLite once every 1.5s and broadcasts ticks to all connected mobile clients.
- **MT5 Alignment**: Sizing, margins, and floating metrics strictly follow MetaTrader 5 account standards.

---

## 🚀 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Gateway healthcheck & database status |
| `GET` | `/api/v1/state` | MT5 Account Metrics (Balance, Equity, Margin, Free Margin, Win Rate, ROI) |
| `GET` | `/api/v1/positions` | Active hedged positions, hold duration, floating gross/net |
| `GET` | `/api/v1/trades` | Paginated completed trades with filter (`ALL`, `WIN`, `LOSS`) |
| `GET` | `/api/v1/trades/daily` | Calendar summary aggregated by date |
| `GET` | `/api/v1/quotes` | Market radar pair universe, spreads, and entry flags |
| `GET` | `/api/v1/funding` | Historical funding rate payments per exchange |

---

## ⚡ WebSocket Streaming Protocol

- **Endpoint**: `/ws/stream`
- **Client Heartbeat**: Send `{"event": "ping"}` $\rightarrow$ Server responds `{"event": "pong"}`
- **Tick Event (every 1.5s)**:
```json
{
  "event": "tick",
  "timestamp": "2026-10-28 08:30:00",
  "data": {
    "account": {
      "balance": 29.9026,
      "equity": 29.9311,
      "margin_used": 18.0,
      "free_margin": 11.9026,
      "margin_level_pct": 166.3,
      "win_rate_pct": 94.1,
      "total_trades": 17
    },
    "positions": [...],
    "opportunities_count": 3,
    "active_slots_used": 3,
    "max_slots": 3
  }
}
```

---

## 🛠️ Deploying on STB as Systemd Service

1. Copy backend directory to STB:
   ```bash
   scp -r backend root@100.125.199.11:/root/funding-arb-pwa/
   ```
2. Create service file `/etc/systemd/system/funding-api.service`:
   ```ini
   [Unit]
   Description=Funding Arbitrage MT5 Gateway API
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/funding-arb-pwa/backend
   Environment=DB_PATH=/root/funding-arb/data/arbitrage.db
   Environment=PORT=8000
   Environment=HOST=0.0.0.0
   ExecStart=/root/spot-transfer-arbitrage/.venv/bin/python3 run.py
   Restart=always
   RestartSec=3

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start:
   ```bash
   systemctl daemon-reload
   systemctl enable --now funding-api.service
   ```
