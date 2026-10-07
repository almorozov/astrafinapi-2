#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
PID_FILE="${PID_FILE:-$APP_DIR/astrafinapi.pid}"
LOG_FILE="${LOG_FILE:-$APP_DIR/astrafinapi.log}"
PORT="${PORT:-7000}"
HOST="${HOST:-0.0.0.0}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

cd "$APP_DIR"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "[start] already running, pid=$(cat "$PID_FILE")"
  exit 0
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[start] creating venv at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
fi

if [[ -z "${JWT_SECRET:-}" ]]; then
  export JWT_SECRET="$(head -c 32 /dev/urandom | base64)"
  echo "[start] generated ephemeral JWT_SECRET"
fi

export DATABASE_URL="${DATABASE_URL:-sqlite:///$APP_DIR/astra.db}"

nohup "$VENV_DIR/bin/uvicorn" app.main:app \
  --host "$HOST" --port "$PORT" \
  >>"$LOG_FILE" 2>&1 &

echo $! > "$PID_FILE"
echo "[start] pid=$(cat "$PID_FILE") port=$PORT db=$DATABASE_URL"
echo "[start] log=$LOG_FILE"

# короткая проверка готовности
for _ in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    echo "[start] ok"
    exit 0
  fi
  sleep 0.5
done

echo "[start] WARN: healthcheck did not pass in 10s, see $LOG_FILE" >&2
exit 1