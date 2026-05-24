# Angel One Index Algo Trading Platform

Production-oriented fullstack algorithmic trading application for Indian index options on NIFTY and BANKNIFTY using Angel One SmartAPI.

The platform supports:

- Paper trading with simulated orders, PnL, virtual execution, and persistent trade records.
- Live trading through an isolated Angel One SmartAPI broker service.
- Intraday momentum breakout strategy with EMA, RSI, VWAP, Supertrend, volume breakout, and 15-minute trend confirmation.
- Strict risk management for max daily loss, per-trade loss/target, duplicate signal prevention, concurrent positions, and market-close exits.
- React dashboard with TradingView Lightweight Charts, strategy controls, live PnL, positions, trade history, alerts, logs, and websocket updates.
- FastAPI backend with PostgreSQL, Redis, Celery, Docker, Nginx, and tests.

## Repository layout

```text
backend/
  app/
    api/           FastAPI routes and websocket endpoint
    broker/        Angel One SmartAPI integration boundary
    indicators/    EMA, RSI, VWAP, ATR, Supertrend
    models/        SQLAlchemy database tables
    orders/        Paper/live order execution service
    risk/          Risk engine
    scheduler/     Celery tasks
    services/      Auth, alerts, reports, market data, backtesting
    strategy/      Momentum breakout and option selection
    websocket/     Realtime connection manager
  tests/
frontend/
  src/
    components/    Dashboard widgets
    hooks/         Websocket hook
    store.ts       Zustand store
infra/
docs/
scripts/
```

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Dashboard: <http://localhost:3000>
- Gateway: <http://localhost>
- Backend health: <http://localhost/health>
- Swagger UI: <http://localhost/docs>

## Development

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run build
```

## Vercel frontend deployment

The React dashboard can be deployed to Vercel from the repository root using `vercel.json`.

Set these Vercel environment variables to point the dashboard at a separately hosted FastAPI backend:

```text
VITE_API_URL=https://your-backend.example.com/api/v1
VITE_WS_URL=wss://your-backend.example.com/api/v1/ws
```

CLI deployment:

```bash
export VERCEL_TOKEN=your-token
./scripts/deploy-vercel.sh
```

See [Vercel deployment](docs/VERCEL.md) for details.

## Safety defaults

The app defaults to `paper` mode. Paper mode never calls Angel One order APIs. Live mode requires SmartAPI credentials in `.env` and should only be enabled after verifying instrument symbols, expiry selection, and broker tokens.

## Documentation

- [API documentation](docs/API.md)
- [Deployment guide](docs/DEPLOYMENT.md)
- [Strategy execution flow](docs/STRATEGY_FLOW.md)
- [Vercel deployment](docs/VERCEL.md)

## Tests

Current tests cover:

- Momentum breakout CE signal generation.
- Risk engine entry-window and duplicate-signal controls.

Run backend tests with:

```bash
cd backend
pytest
```
