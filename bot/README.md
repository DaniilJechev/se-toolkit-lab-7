# LMS Telegram Bot

Telegram bot for LMS Analytics - Lab 7 project.

## Features

- `/start` - Welcome message
- `/help` - Available commands
- `/health` - System status
- `/labs` - List available labs
- `/scores [lab]` - Check scores
- `/submissions [lab]` - View submissions

## Installation

```bash
uv sync
```

## Usage

### Test Mode

```bash
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
```

### Telegram Mode

```bash
# Set environment variables in .env.bot.secret
uv run bot.py
```

## Configuration

Copy `.env.bot.example` to `.env.bot.secret` and fill in:

- `BOT_TOKEN` - Telegram bot token from @BotFather
- `LMS_API_URL` - LMS backend URL
- `LMS_API_KEY` - LMS API key
- `LLM_API_KEY` - LLM API key
- `LLM_API_BASE_URL` - LLM endpoint
- `LLM_API_MODEL` - Model name
