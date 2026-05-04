# KPIs & Definitions

The optimization loop only works if numerators and denominators are agreed. This is the dictionary.

## Funnel KPIs (per source / campaign / agent / state / day)

| KPI | Definition | SQL view |
|---|---|---|
| **Leads** | distinct `leads.id` created in the period | `v_kpi_daily.leads` |
| **Spend** | `ad_spend.spend_amount_cents` summed | `v_kpi_daily.spend_cents` |
| **CPL** | `spend_cents / leads` | `v_kpi_daily.cpl_cents` |
| **Contact rate** | calls with outcome ∈ {`connected`,`appointment_set`,`sold`} / leads with at least one call attempt | computed in BI |
| **Quote rate** | leads with `status='appointment_set'` (we treat held appointment as quote) / contacted | computed in BI |
| **Appointments** | `appointments.status IN ('scheduled','confirmed','completed')` | `v_kpi_daily.appts` |
| **CPA** | `spend_cents / appts` | `v_kpi_daily.cpa_cents` |
| **Show rate** | appointments with `status IN ('confirmed','completed')` / total appointments | computed in BI |
| **Sales / Enrollments** | `enrollments.status IN ('approved','submitted','pending')` | `v_kpi_daily.sales` |
| **Enrollment rate** | sales / appointments-completed | computed in BI |
| **CPS** | `spend_cents / sales` | `v_kpi_daily.cps_cents` |
| **Commission revenue** | `enrollments.commission_amount_cents` summed (only when `commission_paid_at IS NOT NULL`) | `v_kpi_daily.commission_cents` |
| **LTV (12-month)** | per-lead realized commission within 12 months of first contact | computed in BI |
| **ROAS** | revenue / spend, period-aligned | computed in BI |
| **Rapid-disenroll rate** | enrollments with `status='rapid_disenroll'` (cancelled within 90 days) / total enrollments | computed in BI; CMS-sensitive |

## Agent KPIs (per agent / day, week, month)

| KPI | Definition | View |
|---|---|---|
| **Leads assigned** | distinct leads where `assigned_agent_id = agent.id` | `v_agent_funnel.leads_assigned` |
| **Connect rate** | calls with `outcome='connected'` / call attempts | BI |
| **Appointment-set rate** | appointments scheduled / leads contacted | BI |
| **Show rate** | held / scheduled | BI |
| **Close rate** | sales / shows | BI |
| **Compliance flags** | `compliance_audit_events.severity IN ('error','critical')` for the agent | `v_compliance_exceptions` |
| **Avg call duration** | `avg(call_logs.duration_seconds)` | BI |
| **Coaching deltas** | week-over-week change in connect/close | BI |

## Source / channel KPIs

| KPI | Definition |
|---|---|
| **Source-quality score** | weighted average of intent + connect rate + close rate + compliance flag rate |
| **Lead duplicate rate** | duplicate_of leads / total leads, by source |
| **Lead opt-out rate** | leads opted out within 30 days / leads, by source |

A source whose lead opt-out rate exceeds 8% or duplicate rate exceeds 5% is paused for review.

## Compliance KPIs (track and don't optimize against — these have a target ceiling)

| KPI | Target ceiling |
|---|---|
| TPMO-disclaimer-missed events / sales calls | 0% |
| Recording-missing events / sales calls | 0% |
| Opt-out leak events / opt-out events | 0% |
| Unlicensed-state outreach / outbound dials | 0% |
| Multi-TPMO consent integrity failures | 0% |
| Critical events / day | trending to 0; anything > 2 in a day pages on-call |

## Operational KPIs

| KPI | Target |
|---|---|
| Speed-to-lead (form submit → first dial) HOT | ≤ 60 s p95 |
| AI qualification latency | ≤ 4 s p95 |
| Cadence step send latency | ≤ 30 s |
| Recording upload to Supabase from Twilio recording-completed | ≤ 5 min p95 |
| Workflow 10 critical-finding alert latency | ≤ 5 min after detection |

## Pre-AEP readiness KPI

A single composite: percent of pre-launch checklist items green, weighted by criticality.
