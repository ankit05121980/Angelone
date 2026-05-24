#!/usr/bin/env bash
set -euo pipefail

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "VERCEL_TOKEN is required. Create one in Vercel account settings and export it before running this script." >&2
  exit 1
fi

npx vercel deploy --prod --token "$VERCEL_TOKEN"
