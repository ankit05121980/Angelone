from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.broker.base import BrokerClient
from app.config.settings import Settings
from app.models.entities import TradeMode
from app.orders.service import OrderService
from app.risk.engine import RiskEngine
from app.schemas.trading import Candle, OrderRequest
from app.services.alerts import AlertService
from app.strategy.momentum_breakout import MomentumBreakoutStrategy
from app.strategy.option_selection import option_symbol
from app.websocket.manager import manager


class StrategyRunner:
    def __init__(self, db: AsyncSession, settings: Settings, broker: BrokerClient | None = None):
        self.db = db
        self.settings = settings
        self.broker = broker
        self.strategy = MomentumBreakoutStrategy()
        self.risk = RiskEngine(settings)
        self.orders = OrderService(db, broker, AlertService(settings))
        self.enabled = False
        self.mode = TradeMode(settings.default_mode)

    async def set_status(self, enabled: bool, mode: TradeMode | None = None) -> None:
        self.enabled = enabled
        if mode:
            self.mode = mode
        await manager.broadcast("strategy_status", {"enabled": self.enabled, "mode": self.mode.value})

    async def on_candles(self, candles_3m: list[Candle], candles_15m: list[Candle] | None = None) -> None:
        if not self.enabled or not candles_3m:
            return
        symbol = candles_3m[-1].symbol
        signal = self.strategy.evaluate(symbol, candles_3m, candles_15m)
        if signal is None:
            return

        await manager.broadcast("strategy_signal", signal.model_dump(mode="json"))
        option_price = max(signal.entry_price * 0.01, 1)
        decision = self.risk.evaluate_entry(signal, option_price, now=datetime.now())
        if not decision.allowed:
            await manager.broadcast("risk_rejected", {"signal": signal.model_dump(mode="json"), "reason": decision.reason})
            return

        order_request = OrderRequest(
            mode=self.mode,
            signal=signal,
            quantity=decision.quantity,
            option_symbol=option_symbol(signal.symbol, signal.strike, signal.side),
            price=option_price,
        )
        await self.orders.execute_entry(order_request)
        self.risk.register_entry(signal.symbol)
