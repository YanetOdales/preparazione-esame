# Multi-arch base: Debian "bookworm" node image is published for
# linux/amd64, linux/arm64 and linux/arm/v7. No --platform pinning needed —
# `docker compose build` just picks whatever matches the host it runs on.
# Build on the Pi -> arm64 image. Build on your laptop/server -> amd64 image.
FROM node:20-bookworm-slim

# ---- System deps -----------------------------------------------------------
# curl/ca-certificates: installers + healthchecks
# git: opencode often needs it (repo detection, worktrees, skills that clone)
# python3/pip/venv: to run your skill's Python scripts
# build-essential: covers any skill/python package needing to compile a wheel
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---- uv (used by your skill's scripts) -------------------------------------
ENV UV_INSTALL_DIR=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# ---- OpenCode CLI + Telegram bot, both global npm installs -----------------
# (npm's postinstall pulls the correct native binary for the arch this image
# is built on, so this stays portable too)
RUN npm install -g opencode-ai@latest @grinev/opencode-telegram-bot@latest

# ---- Working dir = default OpenCode "project" ------------------------------
WORKDIR /workspace

COPY entrypoint-opencode.sh /usr/local/bin/entrypoint-opencode.sh
COPY entrypoint-bot.sh /usr/local/bin/entrypoint-bot.sh
RUN chmod +x /usr/local/bin/entrypoint-opencode.sh /usr/local/bin/entrypoint-bot.sh

# Default command is overridden per-service in docker-compose.yml
CMD ["opencode", "--version"]
