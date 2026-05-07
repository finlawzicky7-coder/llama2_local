# Roadmap

The MVP ships everything called out in the brief. Here is the recommended next slice of work, in order of leverage.

## Near-term

1. **Streaming Telegram replies** — break long board/debate outputs into chunks under Telegram's 4096-char limit, with optional progressive edits.
2. **Tool-use loop** — let agents call typed tools (create_task, recall_memory, web_search) inside Anthropic's tool-use API instead of relying on freeform synthesis.
3. **Scheduled briefs** — `/brief schedule daily 9am` storing a cron expression in `app_settings`; a worker emits the brief via a Telegram bot DM.
4. **Web search tool for Forge** — add a Bing/Tavily client behind `AIProvider`-shaped tool calls.
5. **Per-agent voice tuning** — temperature, model, and max_tokens per agent stored on the `agents` row.
6. **Dashboard auth** — Supabase email magic-link with `user_permissions` RLS gate, replacing the current "anyone with the URL" assumption.

## Medium-term

7. **Calendar + email integrations** for Atlas/Ledger to schedule and follow up.
8. **Multi-tenant** — workspace boundary keyed by Telegram chat or Supabase org. RLS policies already accept a `tg_id` claim; add a `workspace_id` column.
9. **Slack mirror** — second bot adapter so the same orchestration runs from Slack threads.
10. **Mobile dashboard** — same Next.js app, polished mobile layout.

## Long-term

11. **Autonomous loops** — Ledger continuously scans open tasks, prompts owners for status, escalates blockers.
12. **Vector memory tiers** — recent (in-process LRU), warm (pgvector), cold (compressed summaries) with auto-promotion.
13. **Voice in Telegram** — receive voice notes, transcribe, run as text input.
