# Multi-Funnel Local Business System

Sacramento + Rocklin, CA local service funnels built on shared infrastructure.

## Selected Funnels (Phase 1 winners)

1. **Mid-Term Rentals for Travel Nurses** — highest revenue per lead, lowest local competition
2. **Cleaning / Turnover Services** — fastest speed to revenue, feeds the other funnels

Scaffolded but not launched: Airbnb Co-Hosting, RV Rentals Lead Gen (see `docs/PHASE-1-PRIORITIZATION.md` for the decision).

## Stack

| Layer | Service | Status |
| --- | --- | --- |
| Database | Supabase | schema ready in `infrastructure/supabase/schema.sql` |
| Payments | Stripe | payment-link spec in `infrastructure/stripe/payment-links.md` |
| Email | Gmail | n8n node template in `infrastructure/n8n/` |
| Automation | n8n (preferred) / Zapier | workflows in `infrastructure/n8n/` |
| Deployment | GitHub Pages via Actions | `.github/workflows/deploy.yml` |

## Repo Layout

```
funnels/
  mtr-travel-nurses/     # landing page + capture form
  cleaning-turnover/     # landing page + capture form
shared/
  lead-router.js         # classify + score + route
  lead-scoring.js        # scoring rules per funnel
  supabase-client.js     # shared insert helper
infrastructure/
  supabase/schema.sql    # leads table + policies
  n8n/                   # new-lead workflow + follow-up sequence
  stripe/                # payment-link spec per funnel
docs/                    # phase-by-phase execution notes
.github/workflows/       # static-site deploy
```

## Quickstart

1. Create a Supabase project, run `infrastructure/supabase/schema.sql` in the SQL editor.
2. Copy `.env.example` to `.env` and fill `SUPABASE_URL`, `SUPABASE_ANON_KEY`.
3. Import `infrastructure/n8n/new-lead-workflow.json` into n8n, set credentials.
4. Create the Stripe payment links described in `infrastructure/stripe/payment-links.md`.
5. Enable GitHub Pages → Actions; pushing to `main` deploys the funnel sites.

## Success Metrics

- Daily leads captured per funnel
- Lead → paid conversion rate
- Revenue per funnel per week
- Cross-funnel upsell rate (MTR ↔ Cleaning)
