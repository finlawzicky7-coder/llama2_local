# AgentBoard OS — Architecture

## Goal

A private, Telegram-native multi-agent operating system for a founder. One message in a group triggers a coordinated boardroom of five specialized agents that can think, debate, assign tasks, remember context, and execute.

## High-level flow

```
Telegram group ──▶ Bot (apps/telegram-bot)
                      │
                      ├─▶ command parser  ──▶ orchestrator
                      └─▶ NL router       ──▶ orchestrator
                                              │
                                              ├─▶ memory (pgvector)
                                              ├─▶ ai provider (Claude)
                                              ├─▶ agents (5 personas)
                                              ├─▶ tasks
                                              └─▶ database (Supabase / Postgres)

Dashboard (apps/dashboard) ─── Postgres ─── same database
```

## Component map

| Component | Responsibility |
|-----------|---------------|
| `apps/telegram-bot` | Receive Telegram updates, parse commands, route, format replies, rate limit, admin gate. |
| `apps/dashboard` | Next.js UI for tasks, memory, conversations, agents, logs, settings. |
| `packages/agents` | Agent definitions: id, name, role, personality, system prompt, allowed actions, decision weight, escalation rules. |
| `packages/orchestrator` | Implements single/board/debate/decision/panic/brief orchestration patterns. Persists every run. |
| `packages/memory` | Embedding + pgvector recall, importance scoring, dedup. |
| `packages/database` | Postgres client (postgres-js) and a small typed repo layer. |
| `packages/queue` | BullMQ wrapper with in-process fallback when Redis is unavailable. |
| `packages/ai` | Provider abstraction (Anthropic default, embeddings via OpenAI-compatible). |
| `packages/shared` | Zod schemas, types, Telegram Markdown formatter. |
| `packages/config` | Strict env validation at startup. |

## Orchestration patterns

### Single (`/ask <agent> <msg>`)
1. Load relevant memories (top-k via vector search).
2. Send prompt + memory context to the chosen agent.
3. Persist run, response, tokens, cost.
4. Format and post to Telegram.

### Board (`/board <msg>`)
1. Memory recall.
2. Fan out to all 5 agents in parallel.
3. Collect responses.
4. Send all responses → CEO (Atlas) for synthesis.
5. Send synthesis → Ops (Ledger) for an action plan.
6. Format and post one consolidated message.

### Debate (`/debate <msg>`)
1. Memory recall.
2. Round 1: each agent gives initial position.
3. Round 2: each agent sees the others' positions and critiques them.
4. Round 3: each agent refines.
5. CEO makes final call.
6. Ops produces execution plan.
7. Persist all internal_agent_messages.

### Decision (`/decision <msg>`)
1. Quick fan-out for brief (≤3-bullet) inputs.
2. CEO chooses direction.
3. Ops gives next 3 actions.

### Panic (`/panic <problem>`)
1. CTO diagnoses.
2. CEO sets priority.
3. Ops triages.

### Brief (`/brief`)
1. Pull last-24h conversations + open tasks + recent decisions/memories.
2. CEO summarizes; Ops lists next actions.

Every run writes to `orchestration_runs` (input, mode, status, total_tokens, cost) plus per-agent `agent_responses` and (for debate) `internal_agent_messages`.

## Natural language routing

The router uses a fast rule-based pre-pass (agent name mentions, common verbs) and falls back to a Claude classifier. It returns:

```ts
{
  mode: 'single' | 'board' | 'debate' | 'decision' | 'panic' | 'task' | 'memory',
  agents: AgentId[],
  urgency: 'low' | 'normal' | 'high' | 'urgent',
  store_memory: boolean,
  create_task: boolean,
  reason: string
}
```

## Memory model

Types: `user_preference`, `business_context`, `decision`, `project`, `task`, `contact`, `system_note`, `lesson_learned`.

- Embeddings: 1536-dim by default (`text-embedding-3-small` compatible).
- Importance score 0–1, decays by access recency × type weight.
- Recall = `vector_search(query, top_k=8)` filtered by `expires_at` and minimum cosine similarity.
- Dedup: before inserting, retrieve top-1; if cosine ≥ 0.92, merge instead.

## Task model

Status: `open | in_progress | blocked | done | canceled`. Priority: `low | medium | high | urgent`.
Tasks always have an `agent_id` (owner) and `created_by` (Telegram user). `task_updates` is an immutable audit log.

## Security model

- `TELEGRAM_ADMIN_USER_IDS` is a comma-separated allowlist. Sensitive commands (`/memory`, `/task`, `/done`, `/mode`, `/brief`, dashboard mutations) check it.
- Webhook secret validates `X-Telegram-Bot-Api-Secret-Token`.
- Per-user token-bucket rate limit (default: 20/min).
- Zod validates every command argument and dashboard request body.
- Supabase RLS policies allow only the service role to write; readers must be authenticated admins.
- Errors surface a safe message to Telegram; full trace goes to `system_logs`.
- `packages/config` aborts process startup on any missing required env var.

## Failure behavior

- Agent failure inside a board/debate: continue with the rest, note partial completion, retry once after 1s.
- Claude API failure: exponential backoff (1s, 2s, 4s) up to 3 attempts.
- Supabase failure: log + safe error; do not crash bot.
- Redis missing: queue degrades to in-process direct execution (logged at INFO).

## File layout

```
/apps
  /telegram-bot       (entry: src/index.ts)
  /dashboard          (Next.js app router)

/packages
  /agents             (agent definitions, registry)
  /orchestrator       (run engines)
  /memory             (vector store + recall)
  /database           (postgres client + repos)
  /queue              (bullmq + fallback)
  /ai                 (provider interface + Anthropic adapter)
  /shared             (zod schemas, formatter, types)
  /config             (env validation)

/supabase/migrations  (idempotent SQL)
/supabase/seed.sql    (seed agents)

/infrastructure/docker        (Dockerfiles, compose)
/infrastructure/deploy        (Railway/Render notes)

/docs                 (this file + setup, security, roadmap, command map)
```
