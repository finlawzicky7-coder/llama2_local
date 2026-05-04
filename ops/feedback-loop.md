# AI Optimization Loop

The optimization loop turns the data we collect into bid, copy, scoring, cadence, and routing changes. It runs daily, weekly, and post-AEP. Every change goes through code review and (for compliance-touching changes) compliance review.

## Inputs

- Daily KPIs (`v_kpi_daily`) by campaign/source/state.
- Agent funnel (`v_agent_funnel`).
- Compliance exceptions (`v_compliance_exceptions`).
- Call summaries (`ai_qualification_sessions`, `call_logs.ai_summary`).
- Ad-platform data pulled into `ad_spend` (Google Ads, Meta, YouTube).
- Ad creative variants and their per-variant CTR/CVR.
- Lead source quality drift (intent + connect + close + opt-out by source over rolling 28 days).

## Daily loop (cron 06:00)

A nightly job (extension of workflow 11) runs:

1. **Bid / budget recommendations.** For each Google Ads campaign:
   - Compute 7-day rolling CPL, CPA, CPS, ROAS.
   - If ROAS < 0.7 × target, recommend −20% budget; if > 1.3 × target, recommend +15% budget.
   - Recommendations are written to a `recommendations` table; an analyst approves before pushing to Google Ads via API.
2. **Source quality flags.** Any source with > 8% opt-out rate or > 5% duplicate rate is flagged for review; auto-paused if > 12% opt-out.
3. **Agent coaching.** Each agent gets a one-paragraph daily summary of yesterday's calls (from `call_logs.ai_summary`) plus any compliance flags.
4. **Cadence tuning.** Step-conversion rates per cadence step are computed; any step with > 30% drop-off relative to prior version is flagged for variant test.
5. **Scoring weights.** A weekly job recomputes the contribution of each `fn_score_lead` term by regressing against actual close. Weight changes go through review before deploy — never auto-deployed.

## Weekly loop (Mondays)

- Source-source comparison: which sources convert at lowest CPS, highest LTV, lowest opt-out?
- Variant tests: ad creative, landing page hero, SMS body, email subject, voicemail variant. One variable changed per test.
- Compliance retrospective: any new flag patterns trigger script/template updates.
- Agent leaderboard with quality + compliance + close rate (do not rank on close alone — that creates incentive to cut compliance corners).

## Pre-AEP loop (mid-September)

- Re-tune scoring weights against last AEP's data.
- Update intent-scorer + qualification prompts based on observed lead language patterns.
- Refresh ad creative; rotate fatigued variants out.
- Pre-fund DNC vendor and SMS quotas to AEP volume.
- Stress-test the dialer (synthetic load) to AEP peak.

## Post-AEP loop (mid-December)

- 100% enrollment audit (see `compliance/audit-procedures.md`).
- Detailed source quality re-rank.
- Agent close-rate / compliance-flag matrix → coaching plans.
- Cadence A/B test winners locked in for evergreen + T65.

## Non-negotiable: changes that bypass the loop

These change immediately, no daily-loop wait:

- Any compliance defect → fix and deploy same day.
- Carrier or FMO bulletin requiring marketing change → deploy within 24h.
- New CMS guidance affecting MCMG → deploy within the regulator-stated effective window.
- DNC vendor change in litigator scrubs → propagate immediately to suppression list.

## Non-negotiable: things we do **not** optimize for

- Total dial volume (vanity metric; quality > quantity).
- Time-to-enrollment in the first call (CMS scrutinizes "instant enrollments").
- "Save up to" or "free benefits" ad copy variants — do not test prohibited claims even to learn.
- Removing the TPMO disclaimer to test conversion — do not even ideate this.

## Recommendations table sketch (add to migrations later if you want it persisted)

```sql
create table optimization_recommendations (
  id uuid primary key default uuid_generate_v4(),
  scope text not null,                 -- 'campaign'|'cadence'|'scoring'|'agent'|'source'
  scope_id text not null,
  recommendation text not null,
  rationale text,
  expected_impact jsonb,
  status text default 'pending' check (status in ('pending','approved','rejected','applied','rolled_back')),
  approved_by uuid,
  approved_at timestamptz,
  applied_at timestamptz,
  applied_payload jsonb,
  created_at timestamptz default now()
);
```
