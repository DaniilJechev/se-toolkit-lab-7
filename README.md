# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment
fasdf
1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

This section explains how to deploy the bot using Docker alongside the backend.

### Prerequisites

- Docker and Docker Compose installed on VM
- `.env.docker.secret` configured with required environment variables

### Environment Variables

Add these to `.env.docker.secret`:

```bash
# Bot configuration
BOT_TOKEN=your-telegram-bot-token-from-botfather
LMS_API_KEY=my-secret-api-key
LLM_API_KEY=your-qwen-api-key
LLM_API_MODEL=coder-model
```

### Deploy Steps

1. **Stop the background bot process** (if running):
   ```bash
   pkill -f "bot.py" 2>/dev/null || true
   ```

2. **Navigate to project directory**:
   ```bash
   cd ~/se-toolkit-lab-7
   ```

3. **Build and start all services**:
   ```bash
   docker compose --env-file .env.docker.secret up --build -d
   ```

4. **Verify services are running**:
   ```bash
   docker compose --env-file .env.docker.secret ps
   ```
   
   You should see:
   - `backend` - running
   - `bot` - running
   - `postgres` - running (healthy)
   - `caddy` - running
   - `pgadmin` - running

5. **Check bot logs**:
   ```bash
   docker compose --env-file .env.docker.secret logs bot --tail 20
   ```
   
   Look for:
   - "Application started" or similar startup message
   - No Python tracebacks
   - "HTTP Request: POST .../getUpdates" - bot polling for messages

6. **Verify backend is healthy**:
   ```bash
   curl -sf http://localhost:42002/docs
   ```

### Verify in Telegram

Send these commands to your bot in Telegram:

- `/start` - Welcome message with inline buttons
- `/health` - Backend status
- "what labs are available?" - Natural language query
- "which lab has the lowest pass rate?" - Multi-step reasoning

### Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| Bot container keeps restarting | Check logs: `docker compose logs bot`. Usually missing env var or import error. |
| `/health` fails but worked before | `LMS_API_URL` must be `http://backend:8000` (not localhost:42002). Inside Docker, localhost is the container itself. |
| LLM queries fail but worked before | `LLM_API_BASE_URL` must use `host.docker.internal` (not localhost). The Qwen proxy is on a different Docker network. |
| "BOT_TOKEN is required" error | Bot env vars need to be in `.env.docker.secret`, not just `.env.bot.secret`. |
| Build fails at `uv sync --frozen` | `uv.lock` must be copied in the Dockerfile. Check your COPY commands. |

### Update Deployment

To deploy new code:

```bash
cd ~/se-toolkit-lab-7
git pull
docker compose --env-file .env.docker.secret up --build -d
```
