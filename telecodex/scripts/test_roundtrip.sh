#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi
python3 scripts/emit_event.py --type progress --text "Prueba de progreso desde telecodex"
python3 scripts/emit_event.py --type waiting --text "Responde algo al bot para que aparezca en inbox.jsonl"
python3 scripts/watcher.py --once

echo
echo "Revisa Telegram. Luego responde al bot y ejecuta:"
echo "python3 scripts/watcher.py --once"
echo "cat runtime/inbox.jsonl"
