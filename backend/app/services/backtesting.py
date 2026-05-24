import math

from app.models.entities import OptionSide
from app.schemas.trading import BacktestRequest, BacktestResult
from app.strategy.momentum_breakout import MomentumBreakoutStrategy


class BacktestingService:
    def __init__(self) -> None:
        self.strategy = MomentumBreakoutStrategy()

    def run(self, request: BacktestRequest) -> BacktestResult:
        equity = request.starting_capital
        peak = equity
        returns: list[float] = []
        trades: list[dict[str, float | str]] = []
        equity_curve: list[dict[str, float | str]] = []
        open_trade: dict[str, float | str] | None = None

        for index in range(22, len(request.candles)):
            window = request.candles[: index + 1]
            candle = request.candles[index]
            signal = self.strategy.evaluate(request.symbol, window)

            if open_trade:
                side = open_trade["side"]
                entry = float(open_trade["entry"])
                pnl = candle.close - entry if side == OptionSide.CE.value else entry - candle.close
                if pnl <= -20 or pnl >= 40:
                    equity += pnl
                    returns.append(pnl / max(equity - pnl, 1))
                    open_trade["exit"] = candle.close
                    open_trade["pnl"] = pnl
                    trades.append(open_trade)
                    open_trade = None

            if signal and open_trade is None:
                open_trade = {
                    "entry_time": signal.candle_time.isoformat(),
                    "side": signal.side.value,
                    "entry": signal.entry_price,
                    "strike": signal.strike,
                }

            peak = max(peak, equity)
            equity_curve.append({"time": candle.candle_time.isoformat(), "equity": equity})

        total_pnl = equity - request.starting_capital
        wins = len([trade for trade in trades if float(trade.get("pnl", 0)) > 0])
        win_rate = (wins / len(trades) * 100) if trades else 0
        max_drawdown = self._max_drawdown([float(point["equity"]) for point in equity_curve])
        sharpe = self._sharpe(returns)
        return BacktestResult(
            trades=trades,
            total_pnl=total_pnl,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            equity_curve=equity_curve,
        )

    @staticmethod
    def _max_drawdown(equity_curve: list[float]) -> float:
        peak = -math.inf
        max_dd = 0.0
        for equity in equity_curve:
            peak = max(peak, equity)
            if peak > 0:
                max_dd = min(max_dd, (equity - peak) / peak)
        return abs(max_dd)

    @staticmethod
    def _sharpe(returns: list[float]) -> float:
        if len(returns) < 2:
            return 0
        mean = sum(returns) / len(returns)
        variance = sum((item - mean) ** 2 for item in returns) / (len(returns) - 1)
        std = math.sqrt(variance)
        return 0 if std == 0 else (mean / std) * math.sqrt(252)
