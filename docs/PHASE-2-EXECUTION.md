# Phase 2 — Parallel Execution

For each of the two selected funnels (MTR, Cleaning) the same 5 steps run
in parallel. Both share infrastructure so step 2–4 happen once, not twice.

| Step | MTR | Cleaning | Status |
| --- | --- | --- | --- |
| 1. Landing page built | `funnels/mtr-travel-nurses/` | `funnels/cleaning-turnover/` | ✅ |
| 2. Supabase schema applied | shared | shared | SQL in `infrastructure/supabase/schema.sql` — run once |
| 3. Form → Supabase wired | `script.js` | `script.js` | ✅ |
| 4. Automation workflows | n8n `new-lead-workflow` branches by funnel | same | ✅ |
| 5. Traffic live | see `PHASE-7-TRAFFIC.md` | see `PHASE-7-TRAFFIC.md` | Manual step |

## Operational launch sequence

1. Create Supabase project → run `schema.sql`.
2. Copy anon key + URL into GitHub repo secrets (`SUPABASE_URL`, `SUPABASE_ANON`).
3. Enable GitHub Pages → Source: GitHub Actions.
4. Push `main` → deploy workflow builds both funnels under
   `https://<user>.github.io/<repo>/mtr-travel-nurses/` and `.../cleaning-turnover/`.
5. Point custom domains: `housing.capitolstays.com` → MTR,
   `turnover916.com` → Cleaning (optional but recommended for SEO).
6. Import both n8n workflows, wire credentials, activate.
7. Supabase Database Webhook on `leads` INSERT → n8n `new-lead` webhook URL.
8. Create Stripe payment links (`infrastructure/stripe/payment-links.md`).
9. Run traffic plays in `PHASE-7-TRAFFIC.md`.
