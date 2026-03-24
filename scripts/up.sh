#!/usr/bin/env bash
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p var/log var/run var/cache/ntfy

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

if [ ! -x .venv/bin/python ]; then
  echo "Missing virtualenv. Run ./scripts/bootstrap.sh first."
  exit 1
fi

if ! command -v ntfy >/dev/null 2>&1; then
  echo "Missing ntfy binary. Install ntfy first, then run ./scripts/up.sh again."
  exit 1
fi

if [ -f var/run/ntfy.pid ] && kill -0 "$(cat var/run/ntfy.pid)" 2>/dev/null; then
  echo "ntfy already running."
else
  nohup ntfy serve --config config/ntfy/server.yml >> var/log/ntfy.log 2>&1 &
  echo $! > var/run/ntfy.pid
  echo "Started ntfy."
fi

if [ -f var/run/goblin-api.pid ] && kill -0 "$(cat var/run/goblin-api.pid)" 2>/dev/null; then
  echo "House Goblin already running."
else
  nohup .venv/bin/python services/goblin-api/app.py >> var/log/goblin-api.log 2>&1 &
  echo $! > var/run/goblin-api.pid
  echo "Started House Goblin."
fi

echo "Open http://127.0.0.1:${HOUSE_GOBLIN_PORT:-8787}/ on the Pi."
