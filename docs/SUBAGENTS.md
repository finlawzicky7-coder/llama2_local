# Subagent Roles

These roles describe how to split work when executing against this scaffold.
They map directly to task buckets and can be assigned to Claude subagents,
contractors, or team members.

## 1. Market Agent
**Owns:** demand signals, pricing data, competitor monitoring.
**Weekly output:**
- Furnished Finder average rates near each Sacramento hospital.
- Top 10 Sacramento STR cleaners on GBP: price, reviews, differentiators.
- Travel nurse contract volume trend (r/TravelNursing + Facebook groups).

**Inputs to the system:** recommended pricing changes for
`infrastructure/stripe/payment-links.md` and copy tweaks for landing pages.

## 2. Build Agent
**Owns:** landing pages, Supabase schema, n8n workflows, GitHub Pages deploy.
**Weekly output:**
- Ships any copy/design tweaks approved by the Market Agent.
- Adds SEO landing pages under `/blog/` on each funnel.
- Maintains `shared/lead-router.js` scoring rules as signals are learned.

**Definition of done:** every change committed to this branch, tests run,
deploy workflow green.

## 3. Traffic Agent
**Owns:** SEO content, GBP posts, Facebook group outreach, cold DMs.
**Weekly output:**
- 1 SEO post per funnel.
- 50 cold outreach messages (cleaning).
- 3 Facebook group availability posts (MTR).

Tracks everything with UTMs; no UTMs → untracked effort → dead to analysis.

## 4. Monetization Agent
**Owns:** Stripe payment links, pricing experiments, upsell logic.
**Weekly output:**
- Reads `funnel_events` for `price_variant` data, picks winners.
- Updates `infrastructure/stripe/payment-links.md` and rotates links in
  repo secrets.
- Designs the next upsell experiment.

## 5. Operations Agent
**Owns:** lead triage, follow-up replies, hand-offs to humans (cleaners,
landlords), refund handling.
**Daily output:**
- Review Slack `#leads-hot` channel → call hot leads within 5 minutes.
- Triage `status='contacted'` rows, bump to `qualified` or `lost`.
- Handle cleaning dispatch + key logistics for MTR.

## Task assignment ritual

At the start of each week:
1. Market Agent drops findings in `docs/weekly/<YYYY-MM-DD>.md`.
2. Traffic + Build + Monetization each pick ≤ 2 tasks from the
   experiments queue in `PHASE-8-IMPROVEMENT.md`.
3. Operations Agent sets the weekly lead target (e.g. 20 leads, 4 bookings).
4. Friday retrospective: which metric moved? Which didn't? Who owns the fix?
