#!/bin/sh
set -e
# load .env if present
if [ -f /app/.env ]; then
  export $(cat /app/.env | grep -v '^#' | xargs)
fi
# ensure data dir
mkdir -p /app/data
# start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-9999} --proxy-headers
