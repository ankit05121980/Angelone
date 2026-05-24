from dataclasses import dataclass, field
from datetime import datetime, time

from app.config.settings import Settings
from app.models.entities import IndexSymbol
from app.schemas.trading import RiskDecision, StrategySignal
from app.strategy.option_selection import calculate_quantity


@dataclass
class SymbolRiskState:
    trades_taken: int = 0
    realized_pnl: float = 0
    last_loss_at: datetime | None = None


@dataclass
class RiskState:
    symbols: dict[IndexSymbol, SymbolRiskState] = field(
        default_factory=lambda: {
            IndexSymbol.NIFTY: SymbolRiskState(),
            IndexSymbol.BANKNIFTY: SymbolRiskState(),
        }
    )
    open_positions: int = 0
    processed_signal_keys: set[str] = field(default_factory=set)

    @property
    def day_pnl(self) -> float:
        return sum(item.realized_pnl for item in self.symbols.values())


class RiskEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.state = RiskState()

    def evaluate_entry(self, signal: StrategySignal, option_price: float, now: datetime | None = None) -> RiskDecision:
        timestamp = now or datetime.now()
        symbol_state = self.state.symbols[signal.symbol]

        if not self._within_entry_window(timestamp.time()):
            return RiskDecision(allowed=False, reason="Outside entry window")

        if self.state.day_pnl <= -abs(self.settings.max_daily_loss):
            return RiskDecision(allowed=False, reason="Maximum daily loss reached")

        if symbol_state.trades_taken >= self.settings.max_trades_per_index:
            return RiskDecision(allowed=False, reason="Maximum trades for index reached")

        if self.state.open_positions >= self.settings.max_concurrent_trades:
            return RiskDecision(allowed=False, reason="Maximum concurrent trades reached")

        signal_key = f"{signal.symbol}:{signal.side}:{signal.candle_time.isoformat()}:{signal.strike}"
        if signal_key in self.state.processed_signal_keys:
            return RiskDecision(allowed=False, reason="Duplicate signal blocked")

        capital = self.settings.nifty_capital if signal.symbol == IndexSymbol.NIFTY else self.settings.banknifty_capital
        quantity = calculate_quantity(signal.symbol, option_price, capital, allocation_pct=0.25)
        capital_used = quantity * option_price

        self.state.processed_signal_keys.add(signal_key)
        return RiskDecision(allowed=True, reason="Risk checks passed", quantity=quantity, capital_used=capital_used)

    def register_entry(self, symbol: IndexSymbol) -> None:
        self.state.symbols[symbol].trades_taken += 1
        self.state.open_positions += 1

    def register_exit(self, symbol: IndexSymbol, pnl: float, exited_at: datetime | None = None) -> None:
        symbol_state = self.state.symbols[symbol]
        symbol_state.realized_pnl += pnl
        self.state.open_positions = max(self.state.open_positions - 1, 0)
        if pnl < 0:
            symbol_state.last_loss_at = exited_at or datetime.now()

    def should_exit_position(self, entry_price: float, last_price: float, quantity: int, now: datetime | None = None) -> tuple[bool, str, float]:
        pnl = (last_price - entry_price) * quantity
        if pnl <= -abs(self.settings.max_loss_per_trade):
            return True, "stoploss", pnl
        if pnl >= self.settings.target_profit_per_trade:
            return True, "target", pnl
        if self._past_force_exit((now or datetime.now()).time()):
            return True, "market_close", pnl
        return False, "hold", pnl

    def _within_entry_window(self, current_time: time) -> bool:
        return self._parse_time(self.settings.entry_start_time) <= current_time <= self._parse_time(self.settings.entry_stop_time)

    def _past_force_exit(self, current_time: time) -> bool:
        return current_time >= self._parse_time(self.settings.force_exit_time)

    @staticmethod
    def _parse_time(value: str) -> time:
        hour, minute = value.split(":", maxsplit=1)
        return time(int(hour), int(minute))
