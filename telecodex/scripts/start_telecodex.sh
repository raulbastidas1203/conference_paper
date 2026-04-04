#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs runtime

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

if [ -f runtime/watcher.pid ] && kill -0 "$(cat runtime/watcher.pid)" 2>/dev/null; then
  echo 'watcher ya está corriendo'
else
  nohup python3 scripts/watcher.py --interval 3 > logs/watcher.log 2>&1 &
  echo $! > runtime/watcher.pid
  echo "watcher pid: $(cat runtime/watcher.pid)"
fi

if [ -f runtime/inbox_sync.pid ] && kill -0 "$(cat runtime/inbox_sync.pid)" 2>/dev/null; then
  echo 'inbox sync ya está corriendo'
else
  nohup python3 scripts/inbox_sync_loop.py --interval 3 > logs/inbox_sync.log 2>&1 &
  echo $! > runtime/inbox_sync.pid
  echo "inbox sync pid: $(cat runtime/inbox_sync.pid)"
fi

if [ -f runtime/command_loop.pid ] && kill -0 "$(cat runtime/command_loop.pid)" 2>/dev/null; then
  echo 'command loop ya está corriendo'
else
  nohup python3 scripts/command_loop.py --interval 3 > logs/command_loop.log 2>&1 &
  echo $! > runtime/command_loop.pid
  echo "command loop pid: $(cat runtime/command_loop.pid)"
fi

echo 'telecodex iniciado'
