from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class IndicatorFrame:
    data: pd.DataFrame

    def latest(self) -> pd.Series:
        if self.data.empty:
            raise ValueError("No indicator data available")
        return self.data.iloc[-1]


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50)


def vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_value = (typical_price * df["volume"]).cumsum()
    cumulative_volume = df["volume"].cumsum().replace(0, np.nan)
    return (cumulative_value / cumulative_volume).ffill()


def atr(df: pd.DataFrame, period: int = 10) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3) -> pd.Series:
    hl2 = (df["high"] + df["low"]) / 2
    atr_values = atr(df, period)
    upper_band = hl2 + multiplier * atr_values
    lower_band = hl2 - multiplier * atr_values

    direction: list[str] = []
    final_upper = upper_band.copy()
    final_lower = lower_band.copy()

    for i in range(len(df)):
        if i == 0:
            direction.append("bullish")
            continue

        if upper_band.iloc[i] < final_upper.iloc[i - 1] or df["close"].iloc[i - 1] > final_upper.iloc[i - 1]:
            final_upper.iloc[i] = upper_band.iloc[i]
        else:
            final_upper.iloc[i] = final_upper.iloc[i - 1]

        if lower_band.iloc[i] > final_lower.iloc[i - 1] or df["close"].iloc[i - 1] < final_lower.iloc[i - 1]:
            final_lower.iloc[i] = lower_band.iloc[i]
        else:
            final_lower.iloc[i] = final_lower.iloc[i - 1]

        if df["close"].iloc[i] > final_upper.iloc[i - 1]:
            direction.append("bullish")
        elif df["close"].iloc[i] < final_lower.iloc[i - 1]:
            direction.append("bearish")
        else:
            direction.append(direction[i - 1])

    return pd.Series(direction, index=df.index)


def add_indicators(candles: pd.DataFrame) -> IndicatorFrame:
    required = {"open", "high", "low", "close", "volume"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing candle columns: {', '.join(sorted(missing))}")

    df = candles.copy()
    df["ema_9"] = ema(df["close"], 9)
    df["ema_21"] = ema(df["close"], 21)
    df["rsi_14"] = rsi(df["close"], 14)
    df["vwap"] = vwap(df)
    df["supertrend_direction"] = supertrend(df, 10, 3)
    df["volume_average_5"] = df["volume"].rolling(window=5).mean().shift(1)
    return IndicatorFrame(df)
