from datetime import datetime

from app.config.settings import Settings
from app.models.entities import IndexSymbol, OptionSide
from app.risk.engine import RiskEngine
from app.schemas.trading import IndicatorSnapshot, StrategySignal


def _signal() -> StrategySignal:
    return StrategySignal(
        symbol=IndexSymbol.NIFTY,
        side=OptionSide.CE,
        candle_time=datetime(2026, 1, 1, 10, 0),
        entry_price=24_500,
        strike=24_500,
        expiry="2026-01-01",
        reason="test",
        indicators=IndicatorSnapshot(
            ema_9=1,
            ema_21=0,
            rsi_14=70,
            vwap=24_400,
            supertrend_direction="bullish",
            volume_average_5=100,
        ),
    )


def test_blocks_entries_outside_trading_window() -> None:
    engine = RiskEngine(Settings())
    decision = engine.evaluate_entry(_signal(), option_price=100, now=datetime(2026, 1, 1, 13, 0))

    assert not decision.allowed
    assert decision.reason == "Outside entry window"


def test_allows_first_valid_entry_and_blocks_duplicate() -> None:
    engine = RiskEngine(Settings())
    now = datetime(2026, 1, 1, 10, 0)

    first = engine.evaluate_entry(_signal(), option_price=100, now=now)
    duplicate = engine.evaluate_entry(_signal(), option_price=100, now=now)

    assert first.allowed
    assert first.quantity > 0
    assert not duplicate.allowed
    assert duplicate.reason == "Duplicate signal blocked"
