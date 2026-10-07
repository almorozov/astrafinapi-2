#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
PID_FILE="${PID_FILE:-$APP_DIR/astrafinapi.pid}"
DB_FILE="${DB_FILE:-$APP_DIR/astra.db}"
#LOG_FILE="${LOG_FILE:-$APP_DIR/astrafinapi.log}"

echo "[restart] stopping astrafinapi"

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    for _ in $(seq 1 20); do
      kill -0 "$PID" 2>/dev/null || break
      sleep 0.25
    done
    if kill -0 "$PID" 2>/dev/null; then
      echo "[restart] force kill $PID"
      kill -9 "$PID" || true
    fi
  fi
  rm -f "$PID_FILE"
fi

pkill -f "uvicorn app.main:app" 2>/dev/null || true

for f in "$DB_FILE" "$DB_FILE-wal" "$DB_FILE-shm" "$DB_FILE-journal"; do
  if [[ -e "$f" ]]; then
    rm -f "$f"
    echo "[restart] removed $f"
  fi
done

#: > "$LOG_FILE" 2>/dev/null || true

#exec "$APP_DIR/start.sh"