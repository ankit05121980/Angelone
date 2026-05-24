from datetime import datetime, timedelta

from app.models.entities import IndexSymbol, OptionSide
from app.schemas.trading import Candle
from app.strategy.momentum_breakout import MomentumBreakoutStrategy


def _bullish_candles() -> list[Candle]:
    base = datetime(2026, 1, 1, 9, 30)
    candles: list[Candle] = []
    price = 24_000.0
    for idx in range(25):
        price += 8
        candles.append(
            Candle(
                symbol=IndexSymbol.NIFTY,
                timeframe="3m",
                candle_time=base + timedelta(minutes=3 * idx),
                open=price - 5,
                high=price + 5 + (20 if idx == 24 else 0),
                low=price - 10,
                close=price + (30 if idx == 24 else 0),
                volume=10_000 + (10_000 if idx == 24 else idx * 100),
            )
        )
    return candles


def test_generates_buy_ce_signal_for_momentum_breakout() -> None:
    signal = MomentumBreakoutStrategy().evaluate(IndexSymbol.NIFTY, _bullish_candles())

    assert signal is not None
    assert signal.side == OptionSide.CE
    assert signal.strike % 50 == 0
