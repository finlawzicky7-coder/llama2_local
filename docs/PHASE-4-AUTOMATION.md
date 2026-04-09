# Phase 4 — Automation

n8n is the orchestrator. Zapier works too — the node shapes translate 1:1,
just replace the Function nodes with Zapier Code steps.

## Trigger map

| Event | Trigger | Workflow |
| --- | --- | --- |
| New lead row | Supabase DB Webhook → n8n `new-lead` | `new-lead-workflow.json` |
| Every hour (follow-ups) | n8n cron | `follow-up-sequence.json` |
| Stripe `checkout.session.completed` | Stripe → n8n `stripe-paid` | update `leads.status = 'paid'`, insert `payments` row |
| Lead score ≥ 70 on INSERT | Inline inside `new-lead-workflow` | Slack alert to `#leads-hot` |

## Email cadence

| Day | MTR | Cleaning |
| --- | --- | --- |
| 0 (immediate) | Intro + 3 matching units | Intro + flat-rate pricing |
| 1 | "Still looking?" + photos | "Adjust scope?" |
| 3 | "Units just freed up" + hold offer | "Same-day slot open" + trial offer |
| 5 | Last-chance + soft close | "Closing out quote" + STAY reply keyword |

## Stop conditions

Any of these halts the sequence by setting `leads.status`:
- Lead replies → `contacted` (manual or via IMAP parser)
- Lead books → `booked`
- Lead pays → `paid`
- No reply after day 5 → `lost`

The hourly cron filter `status = 'new'` skips anything not in the active
pool, so no extra logic is needed.

## Observability

Every touch writes to `public.funnel_events`:
- `view`, `form_submit` → landing page
- `intro_email_sent`, `followup_day1|3|5` → n8n
- `price_variant`, `paid`, `refunded` → Stripe webhook

Query `funnel_events` grouped by `funnel_source, event_type, date_trunc('day', created_at)`
for the daily health dashboard.
