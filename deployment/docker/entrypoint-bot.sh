#!/usr/bin/env bash
set -euo pipefail

: "${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN must be set}"
: "${TELEGRAM_ALLOWED_USER_ID:?TELEGRAM_ALLOWED_USER_ID must be set}"
: "${OPENCODE_API_URL:?OPENCODE_API_URL must be set}"
: "${OPENCODE_MODEL_PROVIDER:?OPENCODE_MODEL_PROVIDER must be set}"
: "${OPENCODE_MODEL_ID:?OPENCODE_MODEL_ID must be set}"
: "${BOT_LOCALE:?BOT_LOCALE must be set}"

CONFIG_DIR="$HOME/.config/opencode-telegram-bot"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/.env" <<EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_ALLOWED_USER_ID=${TELEGRAM_ALLOWED_USER_ID}
OPENCODE_API_URL=${OPENCODE_API_URL}
OPENCODE_MODEL_PROVIDER=${OPENCODE_MODEL_PROVIDER}
OPENCODE_MODEL_ID=${OPENCODE_MODEL_ID}
BOT_LOCALE=${BOT_LOCALE}
EOF

echo "[entrypoint] Waiting for opencode server at ${OPENCODE_API_URL} ..."
until curl -fsS "${OPENCODE_API_URL}/doc" >/dev/null 2>&1 || curl -fsS "${OPENCODE_API_URL}/" >/dev/null 2>&1; do
  echo "[entrypoint] opencode not ready yet, retrying in 2s..."
  sleep 2
done

echo "[entrypoint] Starting opencode-telegram bot..."
exec opencode-telegram start
