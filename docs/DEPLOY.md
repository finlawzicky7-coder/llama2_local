# Deploy

## Railway

1. Create a Railway project; add a **PostgreSQL** plugin (or connect Supabase via `DATABASE_URL`).
2. Add a **Redis** plugin (optional but recommended).
3. Create a service from this repo:
   - Build command: `pnpm install && pnpm --filter telegram-bot build`
   - Start command: `pnpm --filter telegram-bot start`
4. Add env vars from `.env.example`. Set `TELEGRAM_MODE=webhook`, `TELEGRAM_WEBHOOK_URL=https://<your-railway-domain>/telegram/webhook`.
5. Add a second service for the dashboard:
   - Build: `pnpm install && pnpm --filter dashboard build`
   - Start: `pnpm --filter dashboard start`
6. Railway exposes the bot service publicly. Hit `/health` to confirm.
7. Run migrations once: `pnpm db:push` from your local with the production `DATABASE_URL` exported.

## Render

Same shape as Railway. Use a "Web Service" for both bot and dashboard, plus a managed Postgres (with `vector` extension enabled — Render does support `vector`). Bot's health check path: `/health`.

## VPS with Docker Compose

```bash
git clone <this repo>
cd agentboard-os
cp .env.example .env  # fill in
docker compose up -d
```

The compose file builds and runs Postgres+pgvector, Redis, the bot, and the dashboard. The dashboard is exposed on port 3000.

For webhook mode behind a reverse proxy, point your TLS terminator at the bot service on its internal port (defaults to 8080). Set `TELEGRAM_MODE=webhook` and `TELEGRAM_WEBHOOK_URL=https://your-domain/telegram/webhook`.

## Health checks

- Bot: `GET /health` → `{ "ok": true }`
- Dashboard: `GET /` → 200 once Postgres is reachable

## Migrations

Always run `pnpm db:push` after pulling new commits in production. Migrations are idempotent.
