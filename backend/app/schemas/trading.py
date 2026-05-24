from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field

from app.models.entities import IndexSymbol, OptionSide, OrderStatus, PositionStatus, TradeMode


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class Candle(BaseModel):
    symbol: IndexSymbol
    timeframe: str
    candle_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class IndicatorSnapshot(BaseModel):
    ema_9: float
    ema_21: float
    rsi_14: float
    vwap: float
    supertrend_direction: Literal["bullish", "bearish"]
    volume_average_5: float


class StrategySignal(BaseModel):
    symbol: IndexSymbol
    side: OptionSide
    candle_time: datetime
    entry_price: float
    strike: int
    expiry: str
    reason: str
    indicators: IndicatorSnapshot


class RiskDecision(BaseModel):
    allowed: bool
    reason: str
    quantity: int = 0
    capital_used: float = 0


class OrderRequest(BaseModel):
    mode: TradeMode
    signal: StrategySignal
    quantity: int
    option_symbol: str
    price: float


class OrderRead(BaseModel):
    id: str
    mode: TradeMode
    symbol: IndexSymbol
    option_symbol: str
    quantity: int
    price: float
    status: OrderStatus
    broker_order_id: str | None = None

    model_config = {"from_attributes": True}


class PositionRead(BaseModel):
    id: str
    symbol: IndexSymbol
    option_symbol: str
    quantity: int
    average_price: float
    last_price: float
    unrealized_pnl: float
    status: PositionStatus

    model_config = {"from_attributes": True}


class TradeRead(BaseModel):
    id: str
    mode: TradeMode
    symbol: IndexSymbol
    option_symbol: str
    quantity: int
    entry_price: float
    exit_price: float | None
    pnl: float
    status: PositionStatus
    exit_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StrategySettings(BaseModel):
    mode: TradeMode = TradeMode.PAPER
    enabled: bool = False
    max_loss_per_trade: float = 1_000
    target_profit_per_trade: float = 2_000
    max_daily_loss: float = 3_000
    max_trades_per_index: int = 3
    max_concurrent_trades: int = 2


class BacktestRequest(BaseModel):
    symbol: IndexSymbol
    starting_capital: float = 100_000
    candles: list[Candle]


class BacktestResult(BaseModel):
    trades: list[dict[str, Any]]
    total_pnl: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    equity_curve: list[dict[str, float | str]]


class DashboardSummary(BaseModel):
    mode: TradeMode
    strategy_enabled: bool
    live_pnl: float
    day_pnl: float
    win_rate: float
    active_positions: int
    trades_taken: dict[IndexSymbol, int]
