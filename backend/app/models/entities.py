import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class TradeMode(str, enum.Enum):
    PAPER = "paper"
    LIVE = "live"


class IndexSymbol(str, enum.Enum):
    NIFTY = "NIFTY"
    BANKNIFTY = "BANKNIFTY"


class OptionSide(str, enum.Enum):
    CE = "CE"
    PE = "PE"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PLACED = "placed"
    FILLED = "filled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXITED = "exited"


class PositionStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


def uuid_pk() -> Mapped[str]:
    return mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="trader", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Setting(Base, TimestampMixin):
    __tablename__ = "settings"

    id: Mapped[str] = uuid_pk()
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_settings_user_key"),)


class Signal(Base, TimestampMixin):
    __tablename__ = "signals"

    id: Mapped[str] = uuid_pk()
    symbol: Mapped[IndexSymbol] = mapped_column(Enum(IndexSymbol), index=True, nullable=False)
    side: Mapped[OptionSide] = mapped_column(Enum(OptionSide), nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    candle_time: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    strike: Mapped[int] = mapped_column(Integer, nullable=False)
    expiry: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = uuid_pk()
    signal_id: Mapped[str | None] = mapped_column(ForeignKey("signals.id"), nullable=True)
    broker_order_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    mode: Mapped[TradeMode] = mapped_column(Enum(TradeMode), nullable=False)
    symbol: Mapped[IndexSymbol] = mapped_column(Enum(IndexSymbol), index=True, nullable=False)
    option_symbol: Mapped[str] = mapped_column(String(100), nullable=False)
    side: Mapped[str] = mapped_column(String(10), default="BUY", nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    raw_response: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    signal: Mapped[Signal | None] = relationship()


class Trade(Base, TimestampMixin):
    __tablename__ = "trades"

    id: Mapped[str] = uuid_pk()
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False)
    mode: Mapped[TradeMode] = mapped_column(Enum(TradeMode), nullable=False)
    symbol: Mapped[IndexSymbol] = mapped_column(Enum(IndexSymbol), index=True, nullable=False)
    option_symbol: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    status: Mapped[PositionStatus] = mapped_column(Enum(PositionStatus), default=PositionStatus.OPEN, nullable=False)
    exit_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)

    order: Mapped[Order] = relationship()


class Position(Base, TimestampMixin):
    __tablename__ = "positions"

    id: Mapped[str] = uuid_pk()
    trade_id: Mapped[str] = mapped_column(ForeignKey("trades.id"), nullable=False)
    symbol: Mapped[IndexSymbol] = mapped_column(Enum(IndexSymbol), index=True, nullable=False)
    option_symbol: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    average_price: Mapped[float] = mapped_column(Float, nullable=False)
    last_price: Mapped[float] = mapped_column(Float, nullable=False)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    status: Mapped[PositionStatus] = mapped_column(Enum(PositionStatus), default=PositionStatus.OPEN, nullable=False)

    trade: Mapped[Trade] = relationship()


class MarketData(Base):
    __tablename__ = "market_data"

    id: Mapped[str] = uuid_pk()
    symbol: Mapped[IndexSymbol] = mapped_column(Enum(IndexSymbol), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    candle_time: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("symbol", "timeframe", "candle_time", name="uq_market_candle"),)


class StrategyLog(Base):
    __tablename__ = "strategy_logs"

    id: Mapped[str] = uuid_pk()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    symbol: Mapped[IndexSymbol | None] = mapped_column(Enum(IndexSymbol), nullable=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class RiskLog(Base):
    __tablename__ = "risk_logs"

    id: Mapped[str] = uuid_pk()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    symbol: Mapped[IndexSymbol | None] = mapped_column(Enum(IndexSymbol), nullable=True)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class PaperWallet(Base, TimestampMixin):
    __tablename__ = "paper_wallet"

    id: Mapped[str] = uuid_pk()
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=100_000, nullable=False)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    reserved_margin: Mapped[float] = mapped_column(Float, default=0, nullable=False)
