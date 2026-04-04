#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for name in watcher inbox_sync; do
  pidfile="runtime/${name}.pid"
  if [ -f "$pidfile" ]; then
    pid="$(cat "$pidfile")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" || true
      echo "stopped $name ($pid)"
    fi
    rm -f "$pidfile"
  fi
done
