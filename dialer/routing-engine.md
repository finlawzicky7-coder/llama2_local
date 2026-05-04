# Routing Engine

The routing engine answers one question: *given a compliance-cleared lead, who is the right licensed agent to take it right now?*

It runs as `fn_route_lead(lead_id)` in Postgres and is invoked by n8n workflow 05. The function returns either an `agent_id` or `NULL`. NULL means "no eligible agent" — and the lead is moved to nurture, not auto-assigned to anyone unlicensed.

## Eligibility filters (all must pass)

1. `agents.active = true`
2. `agent_licenses.state = lead.state` AND `active = true` AND `expires_at > now()`
3. `agent_carrier_appointments` covers at least one carrier present in `lead.state` (soft filter; warns but does not block in v1)
4. The agent has at least one `skills` element matching the inferred product line:
   - T65 / `medicare_status='turning_65'` → MAPD or MS skill
   - `current_plan_type='MS'` → MS skill
   - `desired_help` contains "drug coverage" → PDP skill
5. Today's assignment count for the agent < `agents.capacity_per_day` (soft cap with hard fallback at 100)
6. The agent's local time is within their working hours (we model this in `agents.timezone` plus a future `working_hours` jsonb if needed)

## Selection

Among eligible agents:

```sql
order by today_count asc,           -- least-loaded first
         last_assigned asc           -- round-robin tiebreak
limit 1
```

This produces a deterministic, fair, and load-aware assignment without any ML.

## Skill / carrier matching (advanced)

Move from soft to hard match by promoting these into the `where` clause once your agent base is large enough that you can be picky:

```sql
and exists (
  select 1 from agent_carrier_appointments aca
  where aca.agent_id = a.id
    and aca.state = v_state
    and aca.active
    and aca.expires_at > current_date
)
```

## What HOT vs WARM vs NURTURE do at routing

- **HOT** — workflow 05 immediately fires workflow 06 (dial) and queues an SMS for parallel delivery (workflow 07 step 0).
- **WARM** — assignment is recorded, but no instant dial. The lead enters cadence (workflow 07) starting at minute 5.
- **NURTURE** — no agent assignment at all (we don't burn agent capacity on cold leads). Email-only drip starts at day 1.

## Round-robin fairness recovery

Every 15 minutes a maintenance job (cron — add as a 12th workflow if/when you scale) rebalances:

- Detects agents with `today_count` ≥ `capacity_per_day` and moves their pending unstarted assignments back into the queue.
- Detects leads sitting unassigned > 5 minutes and re-runs `fn_route_lead`.
- Detects assignments where the agent never made a first-attempt within 10 minutes — escalates and reassigns.

## Reassignment

A lead is reassigned (new `lead_assignments` row, prior row's `unassigned_at` set) when:

- The original agent terminated.
- The original agent has not attempted contact within 60 minutes for HOT or 24 hours for WARM.
- The agent's license in the lead's state expired or was revoked.
- The lead requests a different agent.

## API surface (for ops dashboards)

```sql
-- agents currently in queue, with depth and oldest item age
select a.id, a.full_name,
       count(l.id) filter (where l.status='assigned' and l.assigned_at > now() - interval '24h') as queue,
       extract(epoch from now() - min(l.assigned_at) filter (where l.status='assigned')) as oldest_seconds
from agents a left join leads l on l.assigned_agent_id = a.id
where a.active group by 1,2 order by queue desc;
```

## Anti-patterns (do not implement)

- Don't auto-assign to "any active agent" if no licensed agent is available — that puts the agency on the hook for unlicensed activity.
- Don't sort by `lead_score` first — that starves new agents and creates compliance risk via cherry-picking. Score gates whether to route at all (HOT/WARM/NURTURE), not which agent gets it.
- Don't allow agents to "claim" leads from a shared queue. Push, don't pull. Pull-mode lets bad actors take only the easy ones and skews fairness reports.
