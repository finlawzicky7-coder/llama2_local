# Onboarding CSVs

Fill these out, then run the seed scripts. Order matters: agents → licenses → carrier appointments.

| File | Purpose | Loaded by |
|---|---|---|
| `agents.csv` | One row per active agent | `scripts/seed-agents.sh` |
| `agent_licenses.csv` | One row per agent × state license | `scripts/seed-agents.sh` |
| `agent_carrier_appointments.csv` | One row per agent × carrier × state | `scripts/seed-agents.sh` |
| `state_dnc_subscriptions.csv` | Reference list of state DNC registries to subscribe to | manual |
| `campaigns.csv` | Optional — additional campaigns beyond seed | `scripts/seed-campaigns.sh` |

## Validation rules (the seed script enforces)

- Every `agent_email` must exist in `agents.csv` before being referenced in licenses or carrier appointments.
- `expires_at` must be a future date.
- `state` must be a valid 2-letter USPS code.
- `npn` is optional but recommended; must be unique if present.
- `product_lines` is comma-separated inside the CSV cell, double-quoted.
- The script wraps everything in a transaction. If any row fails validation, nothing is committed.

## How to verify after seed

```sql
-- Count active agents per state with current licensing
select al.state, count(*) as eligible_agents
from agents a
join agent_licenses al on al.agent_id = a.id
where a.active and al.active and al.expires_at > now()
group by al.state order by 1;

-- Identify any state where you plan to acquire leads but have no agent
select 'no_coverage' as alert, c.utm_campaign as campaign
from campaigns c
where active = true
  and not exists (
    select 1 from agent_licenses al join agents a on a.id = al.agent_id
    where al.active and a.active and al.expires_at > now()
  );
```
