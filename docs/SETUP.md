# Setup

## Prerequisites

- Node.js 20+ and pnpm 9 (via `corepack enable`)
- A Postgres instance with the `vector` extension (Supabase project, or local `pgvector/pgvector:pg16` Docker image)
- An Anthropic API key
- A Telegram bot from `@BotFather`
- (Optional) Redis for queueing — falls back to in-process if unset

## 1) Create the Telegram bot

1. Open `@BotFather` on Telegram and run `/newbot`. Note the **token**.
2. Run `/setprivacy` → choose your bot → **Disable**. This lets the bot read group messages instead of only @-mentions.
3. Add the bot to your private group.
4. Find your numeric Telegram user ID (e.g. via `@userinfobot`). You'll add it to `TELEGRAM_ADMIN_USER_IDS`.

## 2) Provision a Postgres + pgvector

### Option A — Supabase (hosted)

1. Create a new Supabase project.
2. SQL Editor → run `create extension if not exists vector;` (the migrations also do this, but enabling once helps).
3. Settings → Database → copy the connection string into `DATABASE_URL`.
4. Settings → API → copy `service_role` and `anon` keys.

### Option B — Local docker

```bash
docker compose up -d postgres
```

The compose file maps Postgres to `localhost:54322` and auto-runs the migrations + seed on first boot.

## 3) Configure environment

```bash
cp .env.example .env
# fill in:
# ANTHROPIC_API_KEY=
# TELEGRAM_BOT_TOKEN=
# TELEGRAM_WEBHOOK_SECRET=  (any random string; required only for webhook mode)
# TELEGRAM_ADMIN_USER_IDS=123456789  (your numeric ID, comma-separated for multiple)
# DATABASE_URL=
# (optional) SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_ANON_KEY
# (optional) REDIS_URL=redis://localhost:6379
# EMBEDDING_API_KEY=  (your OpenAI key, used for text-embedding-3-small)
```

## 4) Install and migrate

```bash
pnpm install
pnpm db:push
```

`db:push` runs every migration in `supabase/migrations/` plus `supabase/seed.sql`. It is idempotent.

## 5) Run

In two terminals:

```bash
# bot (long-polling mode)
pnpm dev:bot

# dashboard
pnpm dev:dashboard
```

Open `http://localhost:3000`. In your Telegram group:

```
/start
/agents
/ask cto Design a scraper for Airbnb owner leads
/board What should I focus on this week?
/debate Hire a sales rep or build a self-serve flow?
/decision Ship v1 next week or pad another sprint?
/task sales high Build cold-DM script for property owners
/tasks
/memory We charge $499/mo for the v1 plan
/recall pricing
/brief
/panic Production webhook is dropping events
```

## 6) Tests

```bash
pnpm test
```

Tests cover the parser, NL router, formatter, agent registry, rate limiter, redactor, memory dedup logic, and the orchestrator flows (with a fake AI provider).

## 7) Production deploy (webhook mode)

Set:

```
TELEGRAM_MODE=webhook
TELEGRAM_WEBHOOK_URL=https://your-domain/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=<long random string>
```

Bot starts a Fastify server on `$PORT` (default 8080), accepts POST `/telegram/webhook`, and sets the webhook with Telegram on boot. Health check: `GET /health`.

See [`docs/DEPLOY.md`](DEPLOY.md) for Railway / Render / VPS instructions.
