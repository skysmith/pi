#!/usr/bin/env bash
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

stop_from_pid() {
  pid_file="$1"
  label="$2"

  if [ ! -f "$pid_file" ]; then
    echo "$label is not running."
    return
  fi

  pid="$(cat "$pid_file")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    echo "Stopped $label."
  else
    echo "$label pid file was stale."
  fi

  rm -f "$pid_file"
}

stop_from_pid var/run/goblin-api.pid "House Goblin"
stop_from_pid var/run/ntfy.pid "ntfy"
