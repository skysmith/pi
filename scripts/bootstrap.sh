#!/usr/bin/env bash
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r services/goblin-api/requirements.txt

mkdir -p var/log var/run var/cache/ntfy

echo "House Goblin bootstrap complete."
