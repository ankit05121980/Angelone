# Strategy Execution Flow

1. Market data enters through Angel One websocket or `/market-data/candles`.
2. 3-minute and 15-minute candles are persisted in PostgreSQL.
3. `MomentumBreakoutStrategy` calculates EMA 9, EMA 21, RSI 14, VWAP, Supertrend (10,3), and previous 5-candle average volume.
4. BUY CE requires:
   - EMA 9 > EMA 21
   - Price > VWAP
   - RSI > 60
   - Supertrend bullish
   - Current candle breaks previous candle high
   - Volume > previous 5-candle average
5. BUY PE mirrors the bearish conditions.
6. Option selection calculates ATM strike, nearest weekly expiry, CE/PE contract symbol, and lot-sized quantity using 25% capital allocation.
7. `RiskEngine` blocks entries outside 09:30-12:30, duplicate signals, excess trades, excess concurrent positions, and daily loss lockouts.
8. Paper mode writes simulated orders/trades only.
9. Live mode calls `AngelOneClient`, places a real order, and can place stoploss/exit orders.
10. Websocket events update dashboard charts, orders, PnL, logs, and strategy status.
11. Exit checks enforce max loss, target profit, and 15:15 market-close force exit.
12. Backtesting replays historical candles and computes PnL, win rate, drawdown, Sharpe ratio, and equity curve.
