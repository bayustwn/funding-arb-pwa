"""
Pydantic Schemas for System & Financial State (MT5 Standard)
"""

from pydantic import BaseModel, Field
from typing import Optional


class AccountMetrics(BaseModel):
    # Core MT5 Account Header Metrics
    balance: float = Field(..., description="Kas Dompet Riil (Bybit Wallet + Binance Wallet)")
    equity: float = Field(..., description="Ekuitas Riil Akun (Balance + Floating Net PnL)")
    margin_used: float = Field(..., description="Total Margin Terkunci di Posisi Aktif")
    free_margin: float = Field(..., description="Sisa Kas Bebas Cair (Balance - Margin)")
    margin_level_pct: Optional[float] = Field(None, description="Margin Level % (Equity / Margin * 100)")

    # Performance & Trade Statistics
    starting_capital: float = Field(..., description="Modal Awal Riil Portofolio")
    realized_trade_pnl: float = Field(..., description="Akumulasi Laba Bersih Trade Tertutup")
    realized_funding_pnl: float = Field(..., description="Akumulasi Potongan/Pendapatan Funding Fee")
    total_realized_profit: float = Field(..., description="Total Laba Realized Bersih (Trade + Funding)")
    floating_market_pnl: float = Field(..., description="Floating PnL Pasar Murni")
    floating_fee_reserve: float = Field(..., description="Cadangan Biaya Fee Putar Balik (PP)")
    floating_net_pnl: float = Field(..., description="Floating Netto Akhir (Pasar + Cadangan Fee PP)")
    net_roi_usd: float = Field(..., description="Net ROI Riil Akun (Equity - Starting Capital)")
    net_roi_pct: float = Field(..., description="Persentase Pertumbuhan Akun")

    # Trade Counter & Win Rate
    total_trades: int = Field(0, description="Total Trade yang Sudah Ditutup")
    winning_trades: int = Field(0, description="Jumlah Trade Menang (Net > 0)")
    losing_trades: int = Field(0, description="Jumlah Trade Kalah (Net <= 0)")
    win_rate_pct: float = Field(0.0, description="Win Rate Persentase")

    # Exchange Specific Balances
    bybit_wallet: float = Field(..., description="Saldo Kas Dompet Bybit")
    bybit_equity: float = Field(..., description="Ekuitas Bybit")
    binance_wallet: float = Field(..., description="Saldo Kas Dompet Binance")
    binance_equity: float = Field(..., description="Ekuitas Binance")

    # Slots Usage
    active_slots_used: int = Field(..., description="Jumlah Slot Posisi yang Sedang Aktif")
    max_slots: int = Field(..., description="Batas Maksimal Slot")


class StateResponse(BaseModel):
    success: bool = True
    server_time: str
    data: AccountMetrics
