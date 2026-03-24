#!/usr/bin/env bash
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

MESSAGE="${1:-House Goblin test ping}"
TITLE="${2:-goblin-test}"
TOPIC="${3:-house}"
API_PORT="${HOUSE_GOBLIN_PORT:-8787}"
MESSAGE_ESCAPED="$(printf '%s' "$MESSAGE" | sed 's/\\/\\\\/g; s/"/\\"/g')"
TITLE_ESCAPED="$(printf '%s' "$TITLE" | sed 's/\\/\\\\/g; s/"/\\"/g')"
TOPIC_ESCAPED="$(printf '%s' "$TOPIC" | sed 's/\\/\\\\/g; s/"/\\"/g')"

curl --fail --silent --show-error \
  -X POST "http://127.0.0.1:${API_PORT}/notify" \
  -H "Content-Type: application/json" \
  -d "{\"topic\":\"${TOPIC_ESCAPED}\",\"title\":\"${TITLE_ESCAPED}\",\"message\":\"${MESSAGE_ESCAPED}\"}"
