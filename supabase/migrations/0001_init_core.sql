-- ============================================================================
-- 0001_init_core.sql
-- Core tables: agents, licenses, leads, consent, opt-outs, calls, AI sessions,
-- appointments, compliance audit events, SOA, enrollments, campaigns, ad spend,
-- recordings, lead assignments.
-- Idempotent — safe to re-run.
-- ============================================================================

create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";
create extension if not exists "citext";

-- ----------------------------------------------------------------------------
-- AGENTS & LICENSING
-- ----------------------------------------------------------------------------
create table if not exists agents (
  id              uuid primary key default uuid_generate_v4(),
  auth_user_id    uuid unique,                       -- maps to auth.users(id)
  full_name       text not null,
  email           citext unique not null,
  phone           text,
  npn             text unique,                       -- National Producer Number
  active          boolean default true,
  hire_date       date,
  termination_date date,
  fmo             text,
  timezone        text default 'America/New_York',
  capacity_per_day int default 40,
  skills          text[] default '{medicare_advantage,medicare_supplement,pdp}',
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

create table if not exists agent_licenses (
  id              uuid primary key default uuid_generate_v4(),
  agent_id        uuid not null references agents(id) on delete cascade,
  state           char(2) not null,                  -- USPS state code
  license_number  text not null,
  loa             text default 'health',             -- line of authority
  active          boolean default true,
  issued_at       date,
  expires_at      date not null,
  created_at      timestamptz default now(),
  unique (agent_id, state, license_number)
);

create table if not exists agent_carrier_appointments (
  id              uuid primary key default uuid_generate_v4(),
  agent_id        uuid not null references agents(id) on delete cascade,
  carrier         text not null,                     -- 'humana','aetna','uhc',...
  state           char(2) not null,
  product_lines   text[] default '{}',               -- 'MA','MAPD','PDP','MS'
  active          boolean default true,
  certified_at    date,
  expires_at      date,
  created_at      timestamptz default now(),
  unique (agent_id, carrier, state)
);

-- ----------------------------------------------------------------------------
-- CAMPAIGNS & AD SPEND
-- ----------------------------------------------------------------------------
create table if not exists campaigns (
  id              uuid primary key default uuid_generate_v4(),
  name            text not null,
  channel         text not null,                     -- google,meta,youtube,seo,referral,directmail,event
  product_focus   text,                              -- MA, MS, PDP, T65, AEP
  utm_source      text,
  utm_medium      text,
  utm_campaign    text,
  active          boolean default true,
  started_at      timestamptz default now(),
  ended_at        timestamptz,
  notes           text,
  created_at      timestamptz default now()
);

create table if not exists ad_spend (
  id              uuid primary key default uuid_generate_v4(),
  campaign_id     uuid references campaigns(id) on delete cascade,
  spend_date      date not null,
  spend_amount_cents bigint not null check (spend_amount_cents >= 0),
  impressions     bigint,
  clicks          bigint,
  raw_payload     jsonb,
  created_at      timestamptz default now(),
  unique (campaign_id, spend_date)
);

-- ----------------------------------------------------------------------------
-- LEADS
-- ----------------------------------------------------------------------------
create table if not exists leads (
  id                  uuid primary key default uuid_generate_v4(),
  first_name          text,
  last_name           text,
  phone               text,                          -- E.164 normalized
  phone_hash          text generated always as (encode(digest(coalesce(phone,''),'sha256'),'hex')) stored,
  email               citext,
  email_hash          text generated always as (encode(digest(lower(coalesce(email::text,'')),'sha256'),'hex')) stored,
  zip_code            text,
  city                text,
  state               char(2),
  timezone            text,
  birth_month         int check (birth_month between 1 and 12),
  birth_year          int check (birth_year between 1900 and extract(year from now())::int),
  medicare_status     text check (medicare_status in (
                        'on_medicare','turning_65','helping_family','disability','unsure','not_eligible'
                      )),
  current_plan_type   text,                          -- 'original','MA','MAPD','MS','PDP','none'
  desired_help        text,                          -- free text from form
  source              text not null,                 -- channel
  campaign_id         uuid references campaigns(id),
  landing_page_url    text,
  utm_source          text,
  utm_medium          text,
  utm_campaign        text,
  utm_content         text,
  utm_term            text,
  referrer_url        text,
  ip_address          inet,
  user_agent          text,
  lead_score          int default 0 check (lead_score between 0 and 100),
  bucket              text default 'nurture' check (bucket in ('hot','warm','nurture','blocked')),
  status              text default 'new' check (status in (
                        'new','pending_compliance','qualifying','assigned','contacted',
                        'appointment_set','no_show','sold','not_interested','dnq','duplicate','blocked'
                      )),
  assigned_agent_id   uuid references agents(id),
  assigned_at         timestamptz,
  consent_valid       boolean default false,
  dnc_status          text default 'unchecked' check (dnc_status in (
                        'unchecked','clear','federal_dnc','state_dnc','litigator','carrier_block','internal_block'
                      )),
  dnc_checked_at      timestamptz,
  opt_out             boolean default false,
  opt_out_at          timestamptz,
  duplicate_of        uuid references leads(id),
  notes               text,
  created_at          timestamptz default now(),
  updated_at          timestamptz default now()
);

-- A lead is reachable iff all four flags align.
create or replace function leads_is_reachable(p_lead leads) returns boolean
language sql stable as $$
  select p_lead.consent_valid
    and p_lead.opt_out is not true
    and p_lead.dnc_status = 'clear';
$$;

-- ----------------------------------------------------------------------------
-- CONSENT EVIDENCE
-- ----------------------------------------------------------------------------
create table if not exists consent_logs (
  id                  uuid primary key default uuid_generate_v4(),
  lead_id             uuid not null references leads(id) on delete cascade,
  consent_type        text not null check (consent_type in (
                        'tcpa_phone','tcpa_sms','email_marketing','tpmo_disclosure',
                        'multi_tpmo_share','recording_notice','soa'
                      )),
  consent_text        text not null,                 -- exact wording shown
  consent_version     text not null,                 -- e.g. 'tpmo-2026-04-01-v3'
  ip_address          inet,
  user_agent          text,
  landing_page_url    text,
  consented_entities  jsonb,                         -- [{name, role, accepted: bool}]
  consent_given       boolean not null,
  evidence_hash       text,                          -- sha256(canonical(payload))
  created_at          timestamptz default now()
);

-- ----------------------------------------------------------------------------
-- OPT-OUTS
-- ----------------------------------------------------------------------------
create table if not exists opt_outs (
  id              uuid primary key default uuid_generate_v4(),
  lead_id         uuid references leads(id) on delete cascade,
  phone           text,
  email           citext,
  channel         text not null check (channel in ('sms','email','phone','voicemail','chat','form','manual','postal')),
  reason          text,
  raw_message     text,
  processed       boolean default false,
  processed_at    timestamptz,
  created_at      timestamptz default now()
);

-- ----------------------------------------------------------------------------
-- DNC CHECK HISTORY (vendor responses retained for audit)
-- ----------------------------------------------------------------------------
create table if not exists dnc_checks (
  id              uuid primary key default uuid_generate_v4(),
  lead_id         uuid references leads(id) on delete cascade,
  phone           text not null,
  vendor          text not null,                     -- 'docusign-dnc','contactcenter','internal'
  result          text not null check (result in ('clear','federal_dnc','state_dnc','litigator','carrier_block','internal_block','error')),
  raw_response    jsonb,
  checked_at      timestamptz default now()
);

-- ----------------------------------------------------------------------------
-- AI QUALIFICATION SESSIONS
-- ----------------------------------------------------------------------------
create table if not exists ai_qualification_sessions (
  id                  uuid primary key default uuid_generate_v4(),
  lead_id             uuid not null references leads(id) on delete cascade,
  channel             text not null check (channel in ('chat','sms','voice','email')),
  model               text,                          -- 'gpt-4.1-mini','claude-sonnet-4-6'
  prompt_version      text,
  transcript          text,
  summary             text,
  intent_score        int check (intent_score between 0 and 100),
  qualified           boolean,
  compliance_flags    jsonb default '[]'::jsonb,
  recommended_next_step text,
  duration_seconds    int,
  cost_usd_cents      int,
  created_at          timestamptz default now()
);

-- ----------------------------------------------------------------------------
-- CALL LOGS & RECORDINGS
-- ----------------------------------------------------------------------------
create table if not exists call_logs (
  id                  uuid primary key default uuid_generate_v4(),
  lead_id             uuid not null references leads(id) on delete cascade,
  agent_id            uuid references agents(id),
  call_provider       text not null,                 -- 'twilio','convoso','justcall'
  provider_call_sid   text unique,
  direction           text check (direction in ('outbound','inbound')),
  from_number         text,
  to_number           text,
  started_at          timestamptz,
  ended_at            timestamptz,
  duration_seconds    int,
  outcome             text check (outcome in (
                        'connected','voicemail','no_answer','busy','failed','dropped',
                        'wrong_number','dnq','appointment_set','sold','not_interested','opt_out'
                      )),
  tpmo_disclaimer_given       boolean default false,
  tpmo_disclaimer_timestamp_s int,                   -- seconds into call
  recording_id        uuid,                          -- forward ref
  transcript          text,
  ai_summary          text,
  notes               text,
  created_at          timestamptz default now()
);

create table if not exists recordings (
  id                  uuid primary key default uuid_generate_v4(),
  call_log_id         uuid unique references call_logs(id) on delete cascade,
  storage_bucket      text not null default 'call-recordings',
  storage_path        text not null,                 -- e.g. 'YYYY/MM/DD/<call_id>.wav'
  duration_seconds    int,
  size_bytes          bigint,
  checksum_sha256     text,
  encryption          text default 'AES-256',
  retention_until     date,                          -- 10 years from call_started
  legal_hold          boolean default false,
  created_at          timestamptz default now()
);

alter table call_logs
  add constraint call_logs_recording_fk
  foreign key (recording_id) references recordings(id) on delete set null
  deferrable initially deferred;

-- ----------------------------------------------------------------------------
-- APPOINTMENTS
-- ----------------------------------------------------------------------------
create table if not exists appointments (
  id              uuid primary key default uuid_generate_v4(),
  lead_id         uuid not null references leads(id) on delete cascade,
  agent_id        uuid references agents(id),
  appointment_time timestamptz not null,
  timezone        text,
  duration_minutes int default 30,
  channel         text default 'phone' check (channel in ('phone','video','in_person')),
  status          text default 'scheduled' check (status in (
                    'scheduled','confirmed','rescheduled','no_show','cancelled','completed'
                  )),
  cal_event_id    text,
  reminder_count  int default 0,
  notes           text,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

-- ----------------------------------------------------------------------------
-- LEAD ASSIGNMENTS (history of every reassignment)
-- ----------------------------------------------------------------------------
create table if not exists lead_assignments (
  id              uuid primary key default uuid_generate_v4(),
  lead_id         uuid not null references leads(id) on delete cascade,
  agent_id        uuid not null references agents(id),
  assigned_at     timestamptz default now(),
  unassigned_at   timestamptz,
  reason          text,                              -- 'speed_to_lead','rebalance','agent_terminated'
  routed_by       text                               -- 'workflow_05','manual'
);

-- ----------------------------------------------------------------------------
-- SOA (Scope of Appointment) records
-- ----------------------------------------------------------------------------
create table if not exists soa_records (
  id              uuid primary key default uuid_generate_v4(),
  lead_id         uuid not null references leads(id) on delete cascade,
  agent_id        uuid not null references agents(id),
  appointment_id  uuid references appointments(id),
  product_types   text[] not null,                   -- 'MA','MAPD','MS','PDP','DSNP','HIP'
  signed_at       timestamptz not null,
  signature_method text check (signature_method in ('electronic','verbal','wet')),
  signature_evidence_url text,                       -- signed URL into Storage
  expires_at      timestamptz,                       -- 12 months from signature is common
  notes           text,
  created_at      timestamptz default now()
);

-- ----------------------------------------------------------------------------
-- ENROLLMENT OUTCOMES
-- ----------------------------------------------------------------------------
create table if not exists enrollments (
  id              uuid primary key default uuid_generate_v4(),
  lead_id         uuid not null references leads(id) on delete cascade,
  agent_id        uuid references agents(id),
  carrier         text not null,
  product_type    text not null,
  plan_id         text,                              -- CMS plan id
  effective_date  date,
  application_id  text,
  status          text default 'submitted' check (status in (
                    'submitted','pending','approved','rejected','withdrawn','rapid_disenroll'
                  )),
  commission_amount_cents bigint,
  commission_paid_at timestamptz,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

-- ----------------------------------------------------------------------------
-- COMPLIANCE AUDIT EVENTS
-- ----------------------------------------------------------------------------
create table if not exists compliance_audit_events (
  id              uuid primary key default uuid_generate_v4(),
  lead_id         uuid references leads(id) on delete set null,
  call_log_id     uuid references call_logs(id) on delete set null,
  agent_id        uuid references agents(id) on delete set null,
  event_type      text not null,                     -- see enum-style list below
  severity        text default 'info' check (severity in ('info','warn','error','critical')),
  result          text not null check (result in ('pass','fail','warning')),
  details         jsonb,
  source_workflow text,                              -- e.g. '02-compliance-gate'
  created_at      timestamptz default now()
);

-- Suggested event_type values (free-text but use these by convention):
--   'consent_recorded','consent_invalid','dnc_pass','dnc_fail',
--   'license_match','license_missing','tpmo_disclaimer_played','tpmo_missing',
--   'recording_uploaded','recording_missing','opt_out_processed',
--   'multi_tpmo_consent_mismatch','retention_expired','rls_violation',
--   'duplicate_lead_merged','prohibited_claim_detected','litigator_flagged'

-- ----------------------------------------------------------------------------
-- SUPPRESSION LIST (litigator + manual block list)
-- ----------------------------------------------------------------------------
create table if not exists suppression_list (
  id              uuid primary key default uuid_generate_v4(),
  phone           text,
  phone_hash      text,
  email           citext,
  email_hash      text,
  reason          text not null,                     -- 'litigator','tcpa_complaint','manual'
  source          text,
  expires_at      timestamptz,
  created_at      timestamptz default now()
);

-- ----------------------------------------------------------------------------
-- updated_at trigger
-- ----------------------------------------------------------------------------
create or replace function set_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

do $$
declare t text;
begin
  for t in
    select unnest(array['agents','leads','appointments','enrollments'])
  loop
    execute format(
      'drop trigger if exists %I_set_updated_at on %I;
       create trigger %I_set_updated_at before update on %I
         for each row execute function set_updated_at();',
      t, t, t, t);
  end loop;
end $$;
