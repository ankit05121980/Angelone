from datetime import date

import pandas as pd

from app.indicators.technical import add_indicators
from app.models.entities import IndexSymbol, OptionSide
from app.schemas.trading import Candle, IndicatorSnapshot, StrategySignal
from app.strategy.option_selection import atm_strike, nearest_weekly_expiry


class MomentumBreakoutStrategy:
    name = "intraday_momentum_breakout"

    def evaluate(self, symbol: IndexSymbol, candles_3m: list[Candle], candles_15m: list[Candle] | None = None) -> StrategySignal | None:
        if len(candles_3m) < 22:
            return None

        df = pd.DataFrame([c.model_dump() for c in candles_3m]).sort_values("candle_time")
        indicator_df = add_indicators(df).data
        latest = indicator_df.iloc[-1]
        previous = indicator_df.iloc[-2]

        trend_ok_ce = True
        trend_ok_pe = True
        if candles_15m and len(candles_15m) >= 22:
            trend_df = pd.DataFrame([c.model_dump() for c in candles_15m]).sort_values("candle_time")
            trend_latest = add_indicators(trend_df).latest()
            trend_ok_ce = trend_latest["ema_9"] > trend_latest["ema_21"] and trend_latest["supertrend_direction"] == "bullish"
            trend_ok_pe = trend_latest["ema_9"] < trend_latest["ema_21"] and trend_latest["supertrend_direction"] == "bearish"

        volume_breakout = latest["volume"] > latest["volume_average_5"]
        indicator_snapshot = IndicatorSnapshot(
            ema_9=float(latest["ema_9"]),
            ema_21=float(latest["ema_21"]),
            rsi_14=float(latest["rsi_14"]),
            vwap=float(latest["vwap"]),
            supertrend_direction=latest["supertrend_direction"],
            volume_average_5=float(latest["volume_average_5"]),
        )

        if (
            trend_ok_ce
            and latest["ema_9"] > latest["ema_21"]
            and latest["close"] > latest["vwap"]
            and latest["rsi_14"] > 60
            and latest["supertrend_direction"] == "bullish"
            and latest["high"] > previous["high"]
            and volume_breakout
        ):
            return self._build_signal(symbol, OptionSide.CE, latest, indicator_snapshot)

        if (
            trend_ok_pe
            and latest["ema_9"] < latest["ema_21"]
            and latest["close"] < latest["vwap"]
            and latest["rsi_14"] < 40
            and latest["supertrend_direction"] == "bearish"
            and latest["low"] < previous["low"]
            and volume_breakout
        ):
            return self._build_signal(symbol, OptionSide.PE, latest, indicator_snapshot)

        return None

    def _build_signal(self, symbol: IndexSymbol, side: OptionSide, latest: pd.Series, indicators: IndicatorSnapshot) -> StrategySignal:
        strike = atm_strike(symbol, float(latest["close"]))
        expiry = nearest_weekly_expiry(date.today()).isoformat()
        return StrategySignal(
            symbol=symbol,
            side=side,
            candle_time=latest["candle_time"],
            entry_price=float(latest["close"]),
            strike=strike,
            expiry=expiry,
            reason=f"{side.value} momentum breakout confirmed on 3m with 15m trend filter",
            indicators=indicators,
        )
