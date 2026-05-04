#!/usr/bin/env bash
# scripts/seed-agents.sh — Load agents.csv + agent_licenses.csv +
# agent_carrier_appointments.csv into Supabase in a single transaction.
#
# Usage:
#   SUPABASE_DB_URL=postgres://... ./scripts/seed-agents.sh \
#     onboarding/agents.csv \
#     onboarding/agent_licenses.csv \
#     onboarding/agent_carrier_appointments.csv

set -euo pipefail

if [[ -z "${SUPABASE_DB_URL:-}" ]]; then
  echo "ERROR: SUPABASE_DB_URL must be set" >&2
  exit 1
fi

agents_csv="${1:-onboarding/agents.csv}"
licenses_csv="${2:-onboarding/agent_licenses.csv}"
carriers_csv="${3:-onboarding/agent_carrier_appointments.csv}"

for f in "$agents_csv" "$licenses_csv" "$carriers_csv"; do
  [[ -f "$f" ]] || { echo "ERROR: missing file $f" >&2; exit 1; }
done

# Build a single transactional script.
tmp=$(mktemp)
trap "rm -f $tmp" EXIT

cat > "$tmp" <<'SQL'
begin;

-- Staging tables
create temp table _stage_agents (
  full_name text, email text, phone text, npn text, fmo text, timezone text,
  capacity_per_day int, skills text
);
create temp table _stage_licenses (
  agent_email text, state text, license_number text, loa text,
  issued_at date, expires_at date
);
create temp table _stage_carriers (
  agent_email text, carrier text, state text, product_lines text,
  certified_at date, expires_at date
);
SQL

# Append \copy commands (these are psql client-side commands, must be on a single line).
echo "\\copy _stage_agents   FROM '$agents_csv'   WITH (FORMAT csv, HEADER true)" >> "$tmp"
echo "\\copy _stage_licenses FROM '$licenses_csv' WITH (FORMAT csv, HEADER true)" >> "$tmp"
echo "\\copy _stage_carriers FROM '$carriers_csv' WITH (FORMAT csv, HEADER true)" >> "$tmp"

cat >> "$tmp" <<'SQL'

-- Validation
do $$
declare missing int;
begin
  -- All license rows reference an agent that exists in the staging set
  select count(*) into missing from _stage_licenses l
   where not exists (select 1 from _stage_agents a where a.email = l.agent_email);
  if missing > 0 then raise exception 'License rows reference unknown agent emails: %', missing; end if;

  select count(*) into missing from _stage_carriers c
   where not exists (select 1 from _stage_agents a where a.email = c.agent_email);
  if missing > 0 then raise exception 'Carrier rows reference unknown agent emails: %', missing; end if;

  -- All expiration dates are in the future
  if exists (select 1 from _stage_licenses where expires_at <= current_date) then
    raise exception 'One or more licenses already expired';
  end if;

  -- All states are 2 letters
  if exists (select 1 from _stage_licenses where length(state) <> 2) then
    raise exception 'License state must be 2-letter USPS code';
  end if;
end $$;

-- Upsert agents
insert into agents (full_name, email, phone, npn, fmo, timezone, capacity_per_day, skills)
select s.full_name, s.email, s.phone, nullif(s.npn,''), nullif(s.fmo,''),
       coalesce(nullif(s.timezone,''),'America/New_York'),
       coalesce(s.capacity_per_day, 40),
       string_to_array(coalesce(nullif(s.skills,''),'medicare_advantage'), ',')
from _stage_agents s
on conflict (email) do update
  set full_name = excluded.full_name,
      phone = excluded.phone,
      npn = excluded.npn,
      fmo = excluded.fmo,
      timezone = excluded.timezone,
      capacity_per_day = excluded.capacity_per_day,
      skills = excluded.skills,
      active = true,
      updated_at = now();

-- Upsert licenses
insert into agent_licenses (agent_id, state, license_number, loa, issued_at, expires_at, active)
select a.id, upper(l.state), l.license_number, coalesce(nullif(l.loa,''),'health'),
       l.issued_at, l.expires_at, true
from _stage_licenses l
join agents a on a.email = l.agent_email
on conflict (agent_id, state, license_number) do update
  set loa = excluded.loa,
      issued_at = excluded.issued_at,
      expires_at = excluded.expires_at,
      active = true;

-- Upsert carrier appointments
insert into agent_carrier_appointments (agent_id, carrier, state, product_lines, certified_at, expires_at, active)
select a.id, lower(c.carrier), upper(c.state),
       string_to_array(coalesce(nullif(c.product_lines,''),''), ','),
       c.certified_at, c.expires_at, true
from _stage_carriers c
join agents a on a.email = c.agent_email
on conflict (agent_id, carrier, state) do update
  set product_lines = excluded.product_lines,
      certified_at = excluded.certified_at,
      expires_at = excluded.expires_at,
      active = true;

-- Coverage report
select '=== State coverage ===' as section;
select al.state, count(distinct a.id) as agents
from agents a join agent_licenses al on al.agent_id = a.id
where a.active and al.active and al.expires_at > current_date
group by al.state order by 1;

select '=== Carrier coverage by state ===' as section;
select aca.state, aca.carrier, count(distinct a.id) as agents
from agents a join agent_carrier_appointments aca on aca.agent_id = a.id
where a.active and aca.active and (aca.expires_at is null or aca.expires_at > current_date)
group by aca.state, aca.carrier order by 1, 2;

commit;
SQL

psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f "$tmp"

echo
echo "Seed complete."
