-- ============================================================================
-- 0002_indexes.sql  — performance indexes
-- ============================================================================

create index if not exists idx_leads_phone           on leads (phone);
create index if not exists idx_leads_phone_hash      on leads (phone_hash);
create index if not exists idx_leads_email_hash      on leads (email_hash);
create index if not exists idx_leads_state           on leads (state);
create index if not exists idx_leads_status          on leads (status);
create index if not exists idx_leads_bucket          on leads (bucket);
create index if not exists idx_leads_assigned_agent  on leads (assigned_agent_id);
create index if not exists idx_leads_campaign        on leads (campaign_id);
create index if not exists idx_leads_created_at      on leads (created_at desc);
create index if not exists idx_leads_dedupe          on leads (phone_hash, email_hash) where duplicate_of is null;

create index if not exists idx_consent_lead          on consent_logs (lead_id, consent_type, created_at desc);
create index if not exists idx_consent_version       on consent_logs (consent_version);

create index if not exists idx_optouts_phone         on opt_outs (phone);
create index if not exists idx_optouts_email         on opt_outs (email);
create index if not exists idx_optouts_lead          on opt_outs (lead_id);
create index if not exists idx_optouts_unprocessed   on opt_outs (processed) where processed = false;

create index if not exists idx_dnc_phone             on dnc_checks (phone, checked_at desc);
create index if not exists idx_dnc_lead              on dnc_checks (lead_id, checked_at desc);

create index if not exists idx_calls_lead            on call_logs (lead_id, started_at desc);
create index if not exists idx_calls_agent           on call_logs (agent_id, started_at desc);
create index if not exists idx_calls_outcome         on call_logs (outcome);
create index if not exists idx_calls_started         on call_logs (started_at desc);

create index if not exists idx_aiqual_lead           on ai_qualification_sessions (lead_id, created_at desc);

create index if not exists idx_appt_time             on appointments (appointment_time);
create index if not exists idx_appt_agent            on appointments (agent_id, appointment_time);
create index if not exists idx_appt_status           on appointments (status);

create index if not exists idx_assign_lead           on lead_assignments (lead_id, assigned_at desc);
create index if not exists idx_assign_agent          on lead_assignments (agent_id, assigned_at desc) where unassigned_at is null;

create index if not exists idx_audit_lead            on compliance_audit_events (lead_id, created_at desc);
create index if not exists idx_audit_type            on compliance_audit_events (event_type, created_at desc);
create index if not exists idx_audit_severity        on compliance_audit_events (severity) where severity in ('error','critical');

create index if not exists idx_licenses_state_active on agent_licenses (state, active, expires_at);
create index if not exists idx_appointments_carrier  on agent_carrier_appointments (carrier, state, active);

create index if not exists idx_recordings_call       on recordings (call_log_id);
create index if not exists idx_recordings_retention  on recordings (retention_until) where legal_hold = false;

create index if not exists idx_suppression_phone_hash on suppression_list (phone_hash);
create index if not exists idx_suppression_email_hash on suppression_list (email_hash);

create index if not exists idx_enrollments_lead      on enrollments (lead_id);
create index if not exists idx_enrollments_agent     on enrollments (agent_id, created_at desc);
create index if not exists idx_enrollments_status    on enrollments (status);

create index if not exists idx_adspend_campaign_date on ad_spend (campaign_id, spend_date);
