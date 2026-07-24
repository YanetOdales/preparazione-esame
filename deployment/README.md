# OpenCode + Telegram bot, self-hosted on the Pi

This repository runs two containers from one image:

- **opencode** — serves OpenCode and executes your skill's `uv`/Python scripts.
- **bot** — runs `opencode-telegram-bot` and talks to Telegram plus the
  sibling `opencode` container over the internal network.

## Quick start

```bash
git clone <wherever you put this folder> opencode-telegram-stack
cd opencode-telegram-stack/deployment
cp .env.example .env
nano .env
```

Edit `.env` with your Telegram bot token, allowed user ID, OpenRouter API key,
and host mount directories.

## Required host directories

```bash
mkdir -p ./data/telegram ./data/esami ./data/opencode/workspace ./data/opencode/root
```

Ensure your local `.agents` directory is available at the path set in
`HOST_AGENTS_DIR`.

## Build and run

```bash
docker compose up -d --build
docker compose logs -f
```

On first boot, `opencode` writes OpenRouter auth and a starter `opencode.json`. 
The bot stores its own runtime `.env` inside the `bot_home` volume, so the container should
start without interactive setup.

Open Telegram and send `/status` to verify the bot can reach the `opencode`
service, then use `/skills` to confirm your skill appears.
