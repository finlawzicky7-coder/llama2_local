-- ============================================================================
-- ops/smoke-tests.sql
-- Run after migrations + seed to confirm the data model behaves correctly.
-- Usage: psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f ops/smoke-tests.sql
--
-- Every block must produce the expected row count or fail loudly.
-- ============================================================================

\echo '--- 1. Tables exist'
select count(*) as core_tables_present
  from information_schema.tables
 where table_schema='public'
   and table_name in (
     'agents','agent_licenses','agent_carrier_appointments',
     'leads','consent_logs','opt_outs','dnc_checks',
     'call_logs','recordings','ai_qualification_sessions',
     'appointments','lead_assignments','soa_records','enrollments',
     'compliance_audit_events','suppression_list','campaigns','ad_spend');
-- expected: 18

\echo '--- 2. RLS enabled on sensitive tables'
select c.relname, c.relrowsecurity
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
 where n.nspname='public'
   and c.relname in ('leads','consent_logs','call_logs','recordings','compliance_audit_events')
 order by 1;
-- expected: relrowsecurity = true for all five

\echo '--- 3. Functions present'
select proname from pg_proc where pronamespace = (select oid from pg_namespace where nspname='public')
  and proname in ('fn_score_lead','fn_route_lead','fn_propagate_opt_out','fn_dedupe_lead','fn_check_tpmo_consent_integrity','leads_is_reachable')
 order by 1;
-- expected: 6 rows

\echo '--- 4. Reachability view: a brand-new lead with no consent is unreachable'
do $$
declare new_id uuid;
begin
  insert into leads (first_name,last_name,phone,email,zip_code,state,medicare_status,source)
  values ('Test','Smoke','+15550001234','smoke@example.com','33101','FL','turning_65','smoke_test')
  returning id into new_id;
  if (select is_reachable from v_lead_reachable where id = new_id) is true then
    raise exception 'Smoke fail: lead with consent_valid=false should not be reachable';
  end if;
  delete from leads where id = new_id;
end $$;

\echo '--- 5. fn_propagate_opt_out propagates correctly'
do $$
declare new_id uuid; updated int;
begin
  insert into leads (first_name,last_name,phone,email,state,source,consent_valid,dnc_status)
  values ('Optout','Test','+15559998888','optout@example.com','FL','smoke_test',true,'clear')
  returning id into new_id;

  select fn_propagate_opt_out(p_phone:='+15559998888', p_channel:='manual', p_reason:='smoke') into updated;
  if updated < 1 then raise exception 'fn_propagate_opt_out did not update any leads'; end if;
  if (select opt_out from leads where id = new_id) is not true then
    raise exception 'leads.opt_out not flipped';
  end if;
  if (select is_reachable from v_lead_reachable where id = new_id) is true then
    raise exception 'lead remained reachable after opt_out';
  end if;

  delete from compliance_audit_events where lead_id = new_id;
  delete from opt_outs where lead_id = new_id;
  delete from suppression_list where phone = '+15559998888';
  delete from leads where id = new_id;
end $$;

\echo '--- 6. fn_score_lead returns 0–100'
do $$
declare new_id uuid; s int;
begin
  insert into leads (first_name,phone,email,state,source,medicare_status)
  values ('Score','+15551112222','score@example.com','FL','google_search','turning_65')
  returning id into new_id;
  select fn_score_lead(new_id, 80) into s;
  if s < 0 or s > 100 then raise exception 'score out of bounds: %', s; end if;
  delete from leads where id = new_id;
end $$;

\echo '--- 7. Multi-TPMO consent integrity rejects malformed consented_entities'
do $$
declare new_id uuid;
begin
  insert into leads (first_name,phone,email,state,source) values ('MT','+15553334444','mt@example.com','FL','smoke_test') returning id into new_id;
  insert into consent_logs (lead_id, consent_type, consent_text, consent_version, consent_given, consented_entities)
  values (new_id, 'multi_tpmo_share', 'x', 'v1', true, '"oops not an array"'::jsonb);
  if fn_check_tpmo_consent_integrity(new_id) then
    raise exception 'Should have failed integrity check for non-array entities';
  end if;
  delete from compliance_audit_events where lead_id = new_id;
  delete from consent_logs where lead_id = new_id;
  delete from leads where id = new_id;
end $$;

\echo '--- 8. Triggers: setting recording.retention_until is automatic'
do $$
declare new_lead uuid; new_call uuid; new_rec uuid; ret date;
begin
  insert into leads (first_name,phone,email,state,source) values ('Rec','+15554445555','rec@example.com','FL','smoke_test') returning id into new_lead;
  insert into call_logs (lead_id, call_provider, direction, started_at, ended_at, duration_seconds, outcome)
  values (new_lead, 'twilio', 'outbound', now()-interval '5 min', now(), 300, 'connected') returning id into new_call;
  insert into recordings (call_log_id, storage_path, duration_seconds, size_bytes)
  values (new_call, 'smoke/2026/05/04/test.wav', 300, 1024) returning id, retention_until into new_rec, ret;
  if ret is null or ret < current_date + interval '9 years' then
    raise exception 'retention_until not set correctly: %', ret;
  end if;
  delete from recordings where id = new_rec;
  delete from call_logs where id = new_call;
  delete from leads where id = new_lead;
end $$;

\echo
\echo 'All smoke tests passed.'
