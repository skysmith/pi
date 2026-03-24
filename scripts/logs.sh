#!/usr/bin/env bash
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

TARGET="${1:-all}"
mkdir -p var/log

case "$TARGET" in
  goblin-api)
    touch var/log/goblin-api.log
    tail -f var/log/goblin-api.log
    ;;
  ntfy)
    touch var/log/ntfy.log
    tail -f var/log/ntfy.log
    ;;
  all)
    touch var/log/goblin-api.log var/log/ntfy.log
    tail -f var/log/goblin-api.log var/log/ntfy.log
    ;;
  *)
    echo "Usage: ./scripts/logs.sh [all|goblin-api|ntfy]"
    exit 1
    ;;
esac
