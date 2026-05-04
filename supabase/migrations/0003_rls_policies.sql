-- ============================================================================
-- 0003_rls_policies.sql
-- Row Level Security: agents see only their leads; service role manages all;
-- compliance role read-only across the board.
-- Assumes Supabase Auth: agent users carry agents.auth_user_id = auth.uid().
-- ============================================================================

-- helper: lookup agents.id by auth.uid()
create or replace function current_agent_id() returns uuid
language sql stable security definer as $$
  select id from agents where auth_user_id = auth.uid() and active = true;
$$;

-- helper: is the caller the service role?
create or replace function is_service_role() returns boolean
language sql stable as $$
  select coalesce(current_setting('request.jwt.claims', true)::jsonb ->> 'role', '') = 'service_role';
$$;

-- helper: is the caller a compliance reviewer?
create or replace function is_compliance_role() returns boolean
language sql stable as $$
  select coalesce(current_setting('request.jwt.claims', true)::jsonb ->> 'role', '') in ('compliance','admin');
$$;

-- enable RLS
alter table agents                   enable row level security;
alter table agent_licenses           enable row level security;
alter table agent_carrier_appointments enable row level security;
alter table leads                    enable row level security;
alter table consent_logs             enable row level security;
alter table opt_outs                 enable row level security;
alter table dnc_checks               enable row level security;
alter table call_logs                enable row level security;
alter table recordings               enable row level security;
alter table ai_qualification_sessions enable row level security;
alter table appointments             enable row level security;
alter table lead_assignments         enable row level security;
alter table soa_records              enable row level security;
alter table enrollments              enable row level security;
alter table compliance_audit_events  enable row level security;
alter table suppression_list         enable row level security;
alter table campaigns                enable row level security;
alter table ad_spend                 enable row level security;

-- ----------------------------------------------------------------------------
-- AGENTS (self-read; service writes; compliance reads)
-- ----------------------------------------------------------------------------
drop policy if exists agents_self_read on agents;
create policy agents_self_read on agents for select
  using (auth_user_id = auth.uid() or is_service_role() or is_compliance_role());

drop policy if exists agents_service_all on agents;
create policy agents_service_all on agents for all
  using (is_service_role()) with check (is_service_role());

-- ----------------------------------------------------------------------------
-- LICENSES & CARRIER APPOINTMENTS (agent self-read, service writes)
-- ----------------------------------------------------------------------------
drop policy if exists licenses_self_read on agent_licenses;
create policy licenses_self_read on agent_licenses for select
  using (agent_id = current_agent_id() or is_service_role() or is_compliance_role());

drop policy if exists licenses_service_all on agent_licenses;
create policy licenses_service_all on agent_licenses for all
  using (is_service_role()) with check (is_service_role());

drop policy if exists carrier_appts_self_read on agent_carrier_appointments;
create policy carrier_appts_self_read on agent_carrier_appointments for select
  using (agent_id = current_agent_id() or is_service_role() or is_compliance_role());

drop policy if exists carrier_appts_service_all on agent_carrier_appointments;
create policy carrier_appts_service_all on agent_carrier_appointments for all
  using (is_service_role()) with check (is_service_role());

-- ----------------------------------------------------------------------------
-- LEADS — agents see only their assigned leads; compliance & service see all
-- ----------------------------------------------------------------------------
drop policy if exists leads_assigned_read on leads;
create policy leads_assigned_read on leads for select
  using (assigned_agent_id = current_agent_id() or is_service_role() or is_compliance_role());

drop policy if exists leads_assigned_update on leads;
create policy leads_assigned_update on leads for update
  using (assigned_agent_id = current_agent_id() or is_service_role())
  with check (assigned_agent_id = current_agent_id() or is_service_role());

drop policy if exists leads_service_insert on leads;
create policy leads_service_insert on leads for insert
  with check (is_service_role());

-- agents may NOT delete leads
drop policy if exists leads_no_delete on leads;
create policy leads_no_delete on leads for delete using (is_service_role());

-- ----------------------------------------------------------------------------
-- CONSENT, DNC, OPT-OUT — service write; assigned agent + compliance read
-- ----------------------------------------------------------------------------
drop policy if exists consent_read on consent_logs;
create policy consent_read on consent_logs for select using (
  is_service_role() or is_compliance_role()
  or exists (select 1 from leads l where l.id = consent_logs.lead_id and l.assigned_agent_id = current_agent_id())
);
drop policy if exists consent_service_write on consent_logs;
create policy consent_service_write on consent_logs for insert with check (is_service_role());

drop policy if exists optout_read on opt_outs;
create policy optout_read on opt_outs for select using (
  is_service_role() or is_compliance_role()
  or exists (select 1 from leads l where l.id = opt_outs.lead_id and l.assigned_agent_id = current_agent_id())
);
drop policy if exists optout_service_write on opt_outs;
create policy optout_service_write on opt_outs for insert with check (is_service_role());

drop policy if exists dnc_read on dnc_checks;
create policy dnc_read on dnc_checks for select using (
  is_service_role() or is_compliance_role()
  or exists (select 1 from leads l where l.id = dnc_checks.lead_id and l.assigned_agent_id = current_agent_id())
);
drop policy if exists dnc_service_write on dnc_checks;
create policy dnc_service_write on dnc_checks for insert with check (is_service_role());

-- ----------------------------------------------------------------------------
-- CALLS, RECORDINGS, AI sessions — agent of the call OR compliance OR service
-- ----------------------------------------------------------------------------
drop policy if exists calls_read on call_logs;
create policy calls_read on call_logs for select using (
  is_service_role() or is_compliance_role()
  or agent_id = current_agent_id()
);
drop policy if exists calls_service_write on call_logs;
create policy calls_service_write on call_logs for insert with check (is_service_role());

drop policy if exists calls_service_update on call_logs;
create policy calls_service_update on call_logs for update using (is_service_role());

drop policy if exists recordings_read on recordings;
create policy recordings_read on recordings for select using (
  is_service_role() or is_compliance_role()
  or exists (select 1 from call_logs c where c.id = recordings.call_log_id and c.agent_id = current_agent_id())
);
drop policy if exists recordings_service_write on recordings;
create policy recordings_service_write on recordings for all
  using (is_service_role()) with check (is_service_role());

drop policy if exists aiqual_read on ai_qualification_sessions;
create policy aiqual_read on ai_qualification_sessions for select using (
  is_service_role() or is_compliance_role()
  or exists (select 1 from leads l where l.id = ai_qualification_sessions.lead_id and l.assigned_agent_id = current_agent_id())
);
drop policy if exists aiqual_service_write on ai_qualification_sessions;
create policy aiqual_service_write on ai_qualification_sessions for insert with check (is_service_role());

-- ----------------------------------------------------------------------------
-- APPOINTMENTS, SOA, ENROLLMENTS — agent on record OR compliance OR service
-- ----------------------------------------------------------------------------
drop policy if exists appt_read on appointments;
create policy appt_read on appointments for select using (
  is_service_role() or is_compliance_role()
  or agent_id = current_agent_id()
);
drop policy if exists appt_service_write on appointments;
create policy appt_service_write on appointments for all
  using (is_service_role() or agent_id = current_agent_id())
  with check (is_service_role() or agent_id = current_agent_id());

drop policy if exists soa_read on soa_records;
create policy soa_read on soa_records for select using (
  is_service_role() or is_compliance_role() or agent_id = current_agent_id()
);
drop policy if exists soa_service_write on soa_records;
create policy soa_service_write on soa_records for insert
  with check (is_service_role() or agent_id = current_agent_id());

drop policy if exists enroll_read on enrollments;
create policy enroll_read on enrollments for select using (
  is_service_role() or is_compliance_role() or agent_id = current_agent_id()
);
drop policy if exists enroll_service_all on enrollments;
create policy enroll_service_all on enrollments for all
  using (is_service_role()) with check (is_service_role());

-- ----------------------------------------------------------------------------
-- ASSIGNMENTS, AUDIT, SUPPRESSION, CAMPAIGNS, AD_SPEND
-- ----------------------------------------------------------------------------
drop policy if exists assign_read on lead_assignments;
create policy assign_read on lead_assignments for select using (
  is_service_role() or is_compliance_role() or agent_id = current_agent_id()
);
drop policy if exists assign_service_all on lead_assignments;
create policy assign_service_all on lead_assignments for all
  using (is_service_role()) with check (is_service_role());

drop policy if exists audit_read on compliance_audit_events;
create policy audit_read on compliance_audit_events for select
  using (is_service_role() or is_compliance_role());
drop policy if exists audit_service_write on compliance_audit_events;
create policy audit_service_write on compliance_audit_events for insert with check (is_service_role());

drop policy if exists suppression_read on suppression_list;
create policy suppression_read on suppression_list for select
  using (is_service_role() or is_compliance_role());
drop policy if exists suppression_service_all on suppression_list;
create policy suppression_service_all on suppression_list for all
  using (is_service_role()) with check (is_service_role());

drop policy if exists campaigns_read on campaigns;
create policy campaigns_read on campaigns for select using (true);
drop policy if exists campaigns_service_all on campaigns;
create policy campaigns_service_all on campaigns for all
  using (is_service_role()) with check (is_service_role());

drop policy if exists adspend_service_all on ad_spend;
create policy adspend_service_all on ad_spend for all
  using (is_service_role() or is_compliance_role()) with check (is_service_role());
