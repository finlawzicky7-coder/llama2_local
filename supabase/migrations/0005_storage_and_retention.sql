-- ============================================================================
-- 0005_storage_and_retention.sql
-- Call-recording storage bucket, retention enforcement, audit triggers.
-- Bucket creation runs via Supabase admin API; SQL here ensures policies
-- assuming the bucket 'call-recordings' exists.
-- ============================================================================

-- Trigger: when a call is logged, set retention_until = started_at + 10 years.
create or replace function fn_set_recording_retention() returns trigger
language plpgsql as $$
begin
  if new.retention_until is null then
    new.retention_until := (current_date + interval '10 years')::date;
  end if;
  return new;
end $$;

drop trigger if exists trg_set_recording_retention on recordings;
create trigger trg_set_recording_retention
before insert on recordings
for each row execute function fn_set_recording_retention();

-- Trigger: when a lead opts out, write an audit event.
create or replace function fn_audit_opt_out() returns trigger
language plpgsql as $$
begin
  if (tg_op = 'UPDATE' and new.opt_out = true and (old.opt_out is distinct from new.opt_out)) then
    insert into compliance_audit_events (lead_id, event_type, result, details, source_workflow)
    values (new.id, 'opt_out_processed','pass',
            jsonb_build_object('previous_status', old.status, 'new_status', new.status),
            'leads-trigger');
  end if;
  return new;
end $$;

drop trigger if exists trg_audit_opt_out on leads;
create trigger trg_audit_opt_out
after update on leads
for each row execute function fn_audit_opt_out();

-- Trigger: every call insert must have tpmo_disclaimer_given resolved by EOD.
-- We don't block insert (call may still be in progress), but we log if false at end.
create or replace function fn_audit_call_disclaimer() returns trigger
language plpgsql as $$
begin
  if (tg_op = 'UPDATE'
      and new.ended_at is not null
      and (old.ended_at is null)
      and new.tpmo_disclaimer_given is not true
      and new.outcome in ('connected','appointment_set','sold')) then
    insert into compliance_audit_events (lead_id, call_log_id, agent_id, event_type, result, severity, details, source_workflow)
    values (new.lead_id, new.id, new.agent_id, 'tpmo_missing','fail','critical',
            jsonb_build_object('outcome', new.outcome, 'duration_s', new.duration_seconds),
            'calls-trigger');
  end if;
  return new;
end $$;

drop trigger if exists trg_audit_call_disclaimer on call_logs;
create trigger trg_audit_call_disclaimer
after update on call_logs
for each row execute function fn_audit_call_disclaimer();

-- Trigger: license expiration soon → emit warning into audit log
create or replace function fn_check_license_expiration() returns trigger
language plpgsql as $$
begin
  if new.expires_at <= current_date + interval '30 days' then
    insert into compliance_audit_events (agent_id, event_type, result, severity, details, source_workflow)
    values (new.agent_id, 'license_expiration_warning','warning','warn',
            jsonb_build_object('state', new.state, 'expires_at', new.expires_at),
            'licenses-trigger');
  end if;
  return new;
end $$;

drop trigger if exists trg_license_expiration on agent_licenses;
create trigger trg_license_expiration
after insert or update on agent_licenses
for each row execute function fn_check_license_expiration();
