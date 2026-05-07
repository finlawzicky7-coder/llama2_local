# AgentBoard OS

A Telegram-native multi-agent company operating system. Drop a single message into a private Telegram group and trigger a coordinated boardroom of five specialized AI agents (CEO, CTO, Sales, Marketing, Ops) that think, debate, assign tasks, remember context, and turn chaos into execution.

This is **not** a chatbot. It is a private command center for a founder/operator.

## What's in here

- **`apps/telegram-bot`** — Telegram bot (long-polling for dev, webhook for prod) with commands, natural-language routing, admin gating, and rate limits.
- **`apps/dashboard`** — Next.js dashboard (Overview, Agents, Tasks, Conversations, Memory, Logs, Settings).
- **`packages/agents`** — The 5 agents (Atlas/CEO, Forge/CTO, Viper/Sales, Nova/Marketing, Ledger/Ops) with full personality definitions.
- **`packages/orchestrator`** — Orchestration engine: single, board, debate, decision, panic, brief.
- **`packages/memory`** — pgvector-backed long-term memory with deduping and importance scoring.
- **`packages/database`** — Supabase / Postgres client, typed access layer.
- **`packages/queue`** — BullMQ wrapper with in-process fallback when Redis is unavailable.
- **`packages/ai`** — Provider abstraction (Anthropic Claude default, swap-able for OpenAI/Google/local).
- **`packages/shared`** — Zod schemas, types, formatters.
- **`packages/config`** — Environment validation.
- **`supabase/migrations`** — All SQL migrations including pgvector setup, RLS, and seed agents.
- **`infrastructure/`** — Docker / docker-compose / deploy notes.
- **`docs/`** — Architecture, data model, agent map, command map, security model.

## Quick start

See [`docs/SETUP.md`](docs/SETUP.md) for the full walkthrough. TL;DR:

```bash
# 1. Install
pnpm install

# 2. Copy env and fill it in (Telegram, Anthropic, Supabase, Redis)
cp .env.example .env

# 3. Push the migrations to Supabase (Postgres + pgvector)
pnpm db:push

# 4. Start Redis (optional — bot falls back to in-process queue)
docker run -p 6379:6379 redis:7-alpine

# 5. Run the bot (long-polling) and dashboard in two terminals
pnpm --filter telegram-bot dev
pnpm --filter dashboard dev
```

Then in your Telegram group: `/start`, `/agents`, `/board What should I do this week?`

## What's fully working

- Five distinct agents with full system prompts and personalities.
- All orchestration modes: `/ask`, `/board`, `/debate`, `/decision`, `/panic`, `/brief`.
- Natural-language routing ("Forge, how do we build this?" → CTO).
- Real Postgres-backed tasks with statuses and priorities.
- pgvector memory with semantic recall and importance scoring.
- Cost tracking per orchestration run.
- Admin-only sensitive commands and per-user rate limiting.
- BullMQ queue with in-process fallback for local dev.
- Next.js dashboard pages for all entities.
- Vitest tests for the parser, router, formatter, agent registry, orchestrator, memory, and tasks.
- Docker Compose for local Postgres+Redis+bot+dashboard.

## What needs real API keys / services

- `ANTHROPIC_API_KEY` — for actual agent responses.
- `TELEGRAM_BOT_TOKEN` — get from @BotFather.
- `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` — or any Postgres with pgvector via `DATABASE_URL`.
- `EMBEDDING_API_KEY` — defaults to OpenAI's embedding endpoint; swap-able.
- `REDIS_URL` — optional, falls back to in-process queue locally.

## Recommended future upgrades

See [`docs/ROADMAP.md`](docs/ROADMAP.md) — calendars/email integrations, agent voice profiles per workspace, multi-tenant, streaming Telegram replies, autonomous agent loops, scheduled briefs, web-search tool use, function-calling tool layer, Slack mirror, mobile dashboard.
