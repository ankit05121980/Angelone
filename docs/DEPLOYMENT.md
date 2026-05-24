# Deployment Guide

## Local Docker deployment

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: <http://localhost:3000>
- Nginx gateway: <http://localhost>
- Backend health: <http://localhost/health>
- API docs: <http://localhost/docs>
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Production checklist

1. Replace `JWT_SECRET` with a long random value.
2. Set strong PostgreSQL credentials and remove public DB/Redis ports.
3. Configure Angel One credentials only in the runtime secret store.
4. Keep `DEFAULT_MODE=paper` until paper execution and broker symbols are verified.
5. Put TLS termination in front of Nginx.
6. Enable persistent volumes and database backups.
7. Monitor backend logs from the `backend_logs` volume.
8. Confirm exchange holidays and broker instrument-token mappings before enabling live mode.

## Angel One SmartAPI setup

Required environment variables:

- `ANGEL_API_KEY`
- `ANGEL_CLIENT_CODE`
- `ANGEL_PASSWORD`
- `ANGEL_TOTP_SECRET`

The broker layer supports login, JWT/feed token storage, historical candles, market orders, stoploss orders, order status, positions, and a websocket stream boundary. Production deployments should plug the broker instrument master into `option_symbol` token resolution before live order placement.
