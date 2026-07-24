#!/usr/bin/env bash
set -euo pipefail

: "${OPENROUTER_API_KEY:?OPENROUTER_API_KEY must be set}"
: "${OPENCODE_MODEL_ID:?OPENCODE_MODEL_ID must be set}"
: "${EXAM_RESULTS_PATH:?EXAM_RESULTS_PATH must be set}"

CONFIG_DIR="$HOME/.config/opencode"
AUTH_DIR="$HOME/.local/share/opencode"
mkdir -p "$CONFIG_DIR" "$AUTH_DIR"

# --- Auth: OpenRouter key ----------------------------------------------------
cat > "$AUTH_DIR/auth.json" <<EOF
{
  "openrouter": {
    "type": "api",
    "key": "${OPENROUTER_API_KEY}"
  }
}
EOF

# --- Provider/model config ---------------------------------------------------
# Only written if it doesn't already exist, so you can hand-edit it later
# (it lives on the opencode_config volume and survives restarts).
if [ ! -f "$CONFIG_DIR/opencode.json" ]; then
  cat > "$CONFIG_DIR/opencode.json" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "provider": {
    "openrouter": {
      "models": {
        "${OPENCODE_MODEL_ID}": {}
      }
    }
  }
}
EOF
fi

# --- Make sure the data dirs your skill scripts expect actually exist -------
mkdir -p "${EXAM_RESULTS_PATH}"

echo "[entrypoint] Global skills visible under: $HOME/.agents/skills"
ls -1 "$HOME/.agents/skills" 2>/dev/null || echo "[entrypoint] (no skills mounted yet at ~/.agents/skills)"

echo "[entrypoint] Starting opencode serve on 0.0.0.0:4096 ..."
exec opencode serve --hostname 0.0.0.0 --port 4096
