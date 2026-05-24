#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Fill Angel One credentials before live trading."
fi

docker compose build
docker compose up -d postgres redis
echo "Core services are ready. Run 'docker compose up' to start the full stack."
