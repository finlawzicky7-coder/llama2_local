# Medicare AI Lead Engine

A compliance-first, AI-powered Medicare lead generation, qualification, appointment-setting, and dialer system. Replaces vendor-bought leads with an owned acquisition machine built on **n8n + Supabase + AI agents + a compliant dialer**.

> **TPMO posture:** This system treats your agency as a Third-Party Marketing Organization (TPMO) under CMS Medicare Communications and Marketing Guidelines (MCMG). Every lead carries documented consent evidence, every Medicare call is recorded in its entirety, the TPMO disclaimer is presented within the first minute of every sales call and prominently on every public surface, and any sharing of beneficiary data with another TPMO requires prior express written consent that itemizes each receiving entity with individual opt-in.

---

## Repository layout

```
docs/                  Architecture, compliance checklist, scaling roadmap
supabase/migrations/   Idempotent SQL migrations (schema, indexes, RLS, views, seed)
n8n/                   11 importable workflow JSON files
ai/prompts/            System prompts for qualification, voice, chat, summarization, audit
landing-pages/         Compliant HTML + consent-tracker.js
dialer/                Dialer state machine, routing engine, recording policy
sales/scripts/         First call, VM, SMS, email, objections, AEP, T65, no-show
compliance/            TPMO disclaimer, consent language, pre-launch checklist, audit
ops/                   KPI definitions, feedback loop, AI optimization spec
```

## Build order (read in this sequence)

1. `docs/01-architecture.md` — full system architecture and data flow
2. `compliance/pre-launch-checklist.md` — must be green before any traffic
3. `supabase/migrations/` — apply 0001 → 0006 in order
4. `landing-pages/` — deploy with consent-tracker.js firing to webhook
5. `n8n/` — import workflows 01 → 11 in order
6. `ai/prompts/` — wire into n8n LLM nodes
7. `dialer/` — configure provider, agent routing, recording, TPMO playback
8. `sales/scripts/` — train agents, lock variants under version control
9. `ops/` — turn on the optimization loop

## Critical compliance rails (do not bypass)

- **Consent gate:** no outreach without `consent_valid = true`, `dnc_status = clear`, `opt_out = false`, **and** an active license in the lead's state.
- **Recording:** every Medicare marketing/sales/enrollment call is recorded end-to-end and retained per CMS guidance (10 years).
- **TPMO disclaimer:** played within the first minute of every sales call, posted prominently on every landing page and ad surface.
- **Multi-TPMO sharing:** if data is shared with another TPMO, the consent UI must list each receiving entity with individual checkboxes — no bundled consent.
- **Opt-out:** any "stop / unsubscribe / remove me / don't call" message — across SMS, email, voice, chat, or form — flips `opt_out = true` and suppresses every channel within minutes.
- **No prohibited claims:** no "best plan," no savings guarantees, no free-benefit bait, no government-affiliation implication.

## Stack

- **Database / auth / storage:** Supabase (Postgres + RLS + Storage for recordings + Edge Functions)
- **Orchestration:** n8n (self-hosted recommended; cloud acceptable)
- **AI:** OpenAI (GPT-4.1 / 4.1-mini) or Anthropic Claude (Sonnet/Haiku) — prompts are model-agnostic
- **Dialer / telephony:** Twilio Programmable Voice or a dialer with native recording + webhook hooks (Convoso, JustCall, etc.)
- **DNC / compliance:** Federal DNC + state DNCs + carrier-specific suppression + internal opt-out table
- **Web:** static landing pages on Cloudflare Pages / Vercel; reCAPTCHA Enterprise
- **Identity / IP:** Cloudflare Turnstile or hCaptcha; client IP + UA captured server-side at webhook

## Disclaimers

This repository is an implementation framework, not legal advice. Final ad copy, landing pages, scripts, disclosure text, retention policies, and workflows must be reviewed by your compliance officer / counsel and your FMO/carriers before launch. Regulations evolve — re-validate before each AEP.
