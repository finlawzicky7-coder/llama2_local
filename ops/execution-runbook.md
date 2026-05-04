# Day 0 → Day 30 Execution Runbook

> A two-week, two-engineer + one-compliance-officer plan to go from this repo to live, compliant lead generation. Dates are calendar days from "Day 0 = kickoff." Owners marked **[ENG]**, **[OPS]**, **[COMPLIANCE]**, **[OWNER]** (the agency owner — only they can sign legal docs and accept money risks).

---

## Day 0 — Kickoff (today)

- [ ] **[OWNER]** Confirm legal entity name, FEIN, primary state, and the 1–3 states you'll launch in.
- [ ] **[OWNER]** Confirm FMO. Pull the FMO contract. Read sections on owned-funnel marketing, lead sharing, and disclosure requirements.
- [ ] **[OWNER]** Decide initial product mix: MAPD only, or MAPD + MS, or all (MAPD + MS + PDP + DSNP).
- [ ] **[ENG]** Fork or pull this repo. `git checkout claude/medicare-ai-lead-engine-cinKO`. Read `README.md` end-to-end.
- [ ] **[COMPLIANCE]** Read `compliance/pre-launch-checklist.md` and `compliance/audit-procedures.md` end-to-end.

---

## Day 1 — Vendor accounts (no commitment to spend yet)

- [ ] **[ENG]** Sign up for: **Supabase** (Pro plan), **n8n Cloud** or self-host, **Twilio**, **OpenAI** (or Anthropic), **Postmark** (or SendGrid), **Cloudflare** (Pages + Turnstile + Workers), **Cal.com**, **Slack** (incoming webhook), **Sentry** (errors).
- [ ] **[ENG]** Pick a domain: `your-agency.com`. Cloudflare DNS, MX records ready.
- [ ] **[OPS]** Open `ops/vendor-matrix.md`. Pick a **DNC vendor** (Contact Center Compliance / Gryphon / DNCcheck). Pick a **voicemail-drop vendor** (Slybroadcast / VoApps RVM). Pick a **transcription vendor** (Deepgram with zero-retention or self-hosted Whisper).
- [ ] **[OWNER]** Authorize a $2k initial test budget (covers vendor setup + first 30 days of low-volume traffic).

Deliverable end of day: every vendor has an account; no money spent beyond setup fees.

---

## Day 2 — Database + auth

- [ ] **[ENG]** `supabase projects create medicare-prod`. Capture connection string.
- [ ] **[ENG]** Apply migrations 0001–0006 (`supabase/README.md`).
- [ ] **[ENG]** Create three storage buckets per `supabase/README.md`. Confirm encryption-at-rest is on.
- [ ] **[ENG]** Create three Supabase Auth roles by JWT claim: `service_role`, `compliance`, `agent`. Issue a service-role key for n8n; issue a compliance JWT for the compliance officer.
- [ ] **[ENG]** Run `scripts/verify-deployment.sh` (in this repo). Every check should pass.

Deliverable end of day: Supabase live, RLS verified, you can run the smoke queries in `ops/smoke-tests.sql`.

---

## Day 3 — n8n + secrets

- [ ] **[ENG]** Stand up n8n at `n8n.your-agency.com`. Use the Docker image with Postgres backing store.
- [ ] **[ENG]** Generate `WEBHOOK_HMAC_SECRET` and `N8N_INTERNAL_TOKEN` (`openssl rand -hex 32` for each). Store in Supabase Vault (production) and `.env` (local).
- [ ] **[ENG]** Populate every variable from `.env.example` in n8n's Variables UI.
- [ ] **[ENG]** Import `n8n/01…11.json`. Activate every workflow.
- [ ] **[ENG]** Hit `POST /webhook/medicare-lead-capture` with a synthetic payload + correct HMAC. Confirm a row lands in `leads`, consent_logs, and triggers the chain.

Deliverable end of day: n8n receives a synthetic lead and the chain runs through the compliance gate.

---

## Day 4 — Twilio + DNC vendor

- [ ] **[OWNER]** Complete Twilio business verification (A2P 10DLC brand registration). This takes 24–72 hours; start now.
- [ ] **[ENG]** Buy 1 outbound voice DID per launch state. Buy 1 SMS sender (toll-free verified or 10DLC) per launch state.
- [ ] **[ENG]** Configure STIR/SHAKEN attestation A on every DID via Twilio Trust Hub.
- [ ] **[ENG]** Sign DNC vendor contract. Get API key. Set `DNC_VENDOR_*` env vars in n8n.
- [ ] **[ENG]** Subscribe to state DNC registries where stricter than federal (Florida, Indiana, Texas at minimum if you operate there).
- [ ] **[COMPLIANCE]** Document litigator-list source. Most DNC vendors include this; confirm with vendor's legal team in writing.

Deliverable end of day: Twilio DIDs live, A2P 10DLC submitted, DNC integration plumbed.

---

## Day 5 — Landing pages

- [ ] **[ENG]** Replace every `{{...}}` token in `landing-pages/*.html`. Use real values: `AGENCY_NAME`, `LICENSE_NUMBERS` (pipe-separated), `ADDRESS`, `PHONE`, `N_CARRIERS`, `N_PLANS`, `TURNSTILE_SITE_KEY`, `CAMPAIGN_ID` (use `select id from campaigns where name='Google Search — Medicare Review';`).
- [ ] **[ENG]** Deploy `landing-pages/` to Cloudflare Pages → `www.your-agency.com`.
- [ ] **[ENG]** Deploy `workers/lead-capture-proxy.ts` as a Cloudflare Worker bound to `www.your-agency.com/api/lead-capture`.
- [ ] **[ENG]** Deploy `workers/twiml-bridge.ts` as a Cloudflare Worker bound to `api.your-agency.com/twiml/medicare-bridge`.
- [ ] **[ENG]** Set Twilio voice URL on the outbound number to `https://api.your-agency.com/twiml/medicare-bridge`.
- [ ] **[COMPLIANCE]** Sign off on the live landing page URL. Capture an HTML snapshot to `consent-evidence` bucket.

Deliverable end of day: a real form on a real domain submits to a real n8n webhook.

---

## Day 6 — Onboard agents + licenses

- [ ] **[OPS]** Fill out `onboarding/agents.csv` with every active agent.
- [ ] **[OPS]** Fill out `onboarding/agent_licenses.csv` — one row per agent × state license.
- [ ] **[OPS]** Fill out `onboarding/agent_carrier_appointments.csv` — one row per agent × carrier × state × product line.
- [ ] **[OPS]** Run `scripts/seed-agent.sh onboarding/agents.csv onboarding/agent_licenses.csv onboarding/agent_carrier_appointments.csv` against the production database.
- [ ] **[OPS]** Have each agent log in via Supabase Auth so `auth_user_id` populates. Verify they see only their own leads in a test query.
- [ ] **[COMPLIANCE]** Spot-check 3 agents — pull their state DOI page and confirm the license number + expiration date in the database matches.

Deliverable end of day: at least one agent licensed in your launch state(s) is callable by the routing engine.

---

## Day 7 — Smoke test (this is the gate)

- [ ] **[ENG]** Run the Day-7 acceptance test from `compliance/pre-launch-checklist.md`:
  - [ ] Submit a real form on the live landing page using your own phone number.
  - [ ] Verify chain: leads → consent_logs → dedupe → DNC → AI qualification → score → route → dial → recording.
  - [ ] Confirm the IVR plays the TPMO disclaimer in the first 60 seconds (listen to the recording).
  - [ ] Verify recording arrives in the `call-recordings` bucket within 5 minutes; checksum matches.
  - [ ] Reply STOP to the SMS. Verify opt-out propagates within 60 seconds.
  - [ ] Trigger workflow 10 manually. Verify Slack digest delivers.
- [ ] **[COMPLIANCE]** Sit in the room for the smoke test. Sign off in writing.

**Do not proceed until the gate is green.**

---

## Day 8–10 — Soft launch (controlled traffic)

- [ ] **[OPS]** Open Google Ads. Create one campaign: "Medicare Review — \[State]" — broad-but-tight keyword set, $50/day, manual CPC, no automated bidding yet.
- [ ] **[OPS]** Add `ad_spend` row daily: `insert into ad_spend (campaign_id, spend_date, spend_amount_cents, impressions, clicks) values (...);` — or wire the Google Ads API into a 12th n8n workflow.
- [ ] **[OPS]** Run on 1 state only. Cap at 20 leads / day.
- [ ] **[COMPLIANCE]** Listen to 100% of recordings for the first 50 calls. Coach in real time.
- [ ] **[ENG]** Watch `compliance_audit_events` and Sentry. Any error stops traffic.

Daily standup at 09:00. Decision at 17:00: continue / pause / fix.

---

## Day 11–14 — Tune

- [ ] **[OPS]** Pull `v_kpi_daily`. Compute baseline CPL, CPA, CPS for the launch state.
- [ ] **[OPS]** Pull `v_compliance_exceptions`. Zero criticals required to proceed.
- [ ] **[ENG]** Adjust `fn_score_lead` weights based on the first 100 leads' actual conversions (record changes in a new migration `0007_score_weights_v2.sql`).
- [ ] **[OPS]** Pause any ad-group with CPL > 3× target or opt-out rate > 8%.
- [ ] **[COMPLIANCE]** Drop call-listening cadence to 1-in-5 once flag rate < 1% sustained for 3 days.

---

## Day 15–21 — Add channels

- [ ] **[OPS]** Launch the T65 funnel (`landing-pages/t65-funnel.html`) targeted at people 64.5–65.0.
- [ ] **[OPS]** Spin up YouTube education channel: 1 video / week, plan-neutral, full TPMO on-screen.
- [ ] **[OPS]** Direct mail QR test: 500 postcards to T65 households in launch state.
- [ ] **[ENG]** Add inbound chat widget on landing pages, wired to `ai/prompts/inbound-chat-agent.md`.

---

## Day 22–28 — Add states

- [ ] **[OWNER]** Confirm next 1–2 states. Verify each agent's licenses in those states; renew or apply where missing.
- [ ] **[ENG]** Per state: spin up dedicated DID + SMS sender, deploy a state-localized landing page variant, add `ad_spend` campaign.
- [ ] **[COMPLIANCE]** Re-walk `compliance/pre-launch-checklist.md` for the new state (state-specific disclosures, recording-consent, DNC).

---

## Day 29–30 — Cadence handoff

- [ ] **[ENG]** Confirm crons: workflow 10 (03:00), workflow 11 (hourly), AI auditor (04:00). All firing reliably.
- [ ] **[COMPLIANCE]** Open `compliance/officer-runbook.md`. Begin daily/weekly/monthly cadence.
- [ ] **[OPS]** Open `ops/feedback-loop.md`. Begin weekly Monday review.
- [ ] **[OWNER]** Schedule recurring monthly review with engineering + compliance to track exceptions, source quality, and capacity.

---

## Hard checkpoints (do not pass without sign-off)

| Checkpoint | Date | Owner | Pass criteria |
|---|---|---|---|
| **Compliance Gate 1** — pre-launch | Day 7 EOD | Compliance Officer | Every box of `pre-launch-checklist.md` green; smoke test signed off in writing |
| **Compliance Gate 2** — soft-launch retrospective | Day 14 EOD | Compliance Officer | Zero critical exceptions over 3 consecutive days; 50+ recordings reviewed; agent flag rate < 1% |
| **Compliance Gate 3** — multi-state | Before Day 22 | Compliance Officer | Per-state checklist green for each new state |
| **Pre-AEP Gate** | Sep 30 of any year | Compliance Officer | Full pre-launch checklist re-run; scripts and templates locked; 3x peak load tested |

---

## What I cannot do for you

These require a human with legal authority and money:

- Sign the FMO contract.
- Sign carrier appointment paperwork.
- Pass state license exams.
- Pay vendor setup fees.
- Authorize ad spend.
- Sign the daily/weekly/quarterly compliance reports.
- Take the legal liability for any beneficiary harm.

Everything else — schemas, scripts, templates, audits, monitoring, dashboards — is in this repo and runnable.
