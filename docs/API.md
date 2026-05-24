# API Documentation

FastAPI serves OpenAPI at `/api/v1/openapi.json` and interactive Swagger UI at `/docs`.

## Core endpoints

- `POST /api/v1/auth/register` - create a user and receive a JWT.
- `POST /api/v1/auth/login` - authenticate and receive a JWT.
- `GET /api/v1/dashboard` - current mode, PnL, win rate, and position counts.
- `GET /api/v1/positions` - active and historical positions.
- `GET /api/v1/trades` - latest trade history.
- `GET /api/v1/orders` - latest orders.
- `PUT /api/v1/strategy/settings` - enable/disable strategy and switch paper/live mode.
- `POST /api/v1/strategy/run-on-candles?symbol=NIFTY` - evaluate stored candles and place an eligible paper/live order.
- `POST /api/v1/market-data/candles` - upsert a candle and broadcast it to dashboards.
- `GET /api/v1/market-data/{symbol}/{timeframe}` - fetch recent candles.
- `POST /api/v1/backtests` - run historical strategy replay.
- `GET /api/v1/reports/trades.csv` - export trades.
- `WS /api/v1/ws` - realtime dashboard events.

## Websocket events

- `candle_update`
- `strategy_signal`
- `risk_rejected`
- `order_update`
- `pnl_update`
- `position_closed`
- `strategy_status`

## Live trading notes

Live order placement is isolated behind `app.broker.AngelOneClient`. Paper mode never calls the broker client and stores simulated orders/trades with `PAPER-*` broker IDs.
