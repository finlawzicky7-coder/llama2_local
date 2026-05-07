# Security Model

## Trust boundaries

1. **Telegram → bot**: validate the secret token on webhook posts. Reject anything else.
2. **User → bot**: gate sensitive commands (`/memory`, `/task`, `/done`, `/mode`, `/brief`) on `TELEGRAM_ADMIN_USER_IDS`.
3. **Bot → AI provider**: send no Telegram tokens, no DB credentials, and no admin user IDs in prompts.
4. **Dashboard → DB**: dashboard runs server-side via Supabase service role; client UI never gets the service role key.

## Rate limiting

Per-user token bucket (default 20 commands / 60s) implemented in `packages/shared/src/rate-limit.ts`. Trips return a friendly Telegram message and a `system_log` entry.

## Input validation

Every command argument and dashboard request body is parsed with Zod in `packages/shared/src/schemas.ts`. Invalid input never reaches the orchestrator.

## Secrets

- Loaded via `packages/config` with `zod`'s `safeParse`; missing required vars abort the process at boot.
- `.env` is `.gitignore`d. `.env.example` ships with placeholders only.
- Logs scrub keys via `redact()` in `packages/shared/src/redact.ts`.

## Database

- Migrations enable RLS on every table.
- Service role used by bot/dashboard server. Anon role gets no insert/update/delete permissions.
- `app_settings` is singleton; updates are only allowed via admin path.

## Webhook hardening

- Use `--set-webhook` with a long random `TELEGRAM_WEBHOOK_SECRET`.
- Strip Telegram-supplied URLs from agent context before sending to Claude.

## What this MVP does NOT defend against

- Multi-tenant attacks (the system is single-org by design).
- Prompt injection from third-party content the user pastes in. Treat external links/text inside prompts as untrusted; `Atlas` is instructed to ignore conflicting "ignore previous instructions" text.
- Telegram account takeover (out of scope; relies on Telegram's auth).
