-- ============================================================================
-- 0004_views_functions.sql
-- Reporting views, scoring function, dedupe function, opt-out propagation,
-- assignment routing helpers.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- VIEW: v_lead_reachable — single source of truth for "may we contact?"
-- ----------------------------------------------------------------------------
create or replace view v_lead_reachable as
select
  l.*,
  (l.consent_valid
    and l.opt_out is not true
    and l.dnc_status = 'clear'
    and not exists (
      select 1 from suppression_list s
       where (s.phone_hash is not null and s.phone_hash = l.phone_hash)
          or (s.email_hash is not null and s.email_hash = l.email_hash)
    )
    and exists (
      select 1 from agent_licenses al
       join agents a on a.id = al.agent_id
       where al.state = l.state and al.active = true and a.active = true
         and al.expires_at > now()
    )
  ) as is_reachable
from leads l;

-- ----------------------------------------------------------------------------
-- VIEW: v_kpi_daily — CPL / CPA / CPS by date and campaign
-- ----------------------------------------------------------------------------
create or replace view v_kpi_daily as
with leads_daily as (
  select date_trunc('day', created_at)::date as d, campaign_id, count(*) as leads
  from leads group by 1,2
),
appts_daily as (
  select date_trunc('day', l.created_at)::date as d, l.campaign_id, count(*) as appts
  from leads l join appointments a on a.lead_id = l.id
  where a.status in ('scheduled','confirmed','completed')
  group by 1,2
),
sales_daily as (
  select date_trunc('day', l.created_at)::date as d, l.campaign_id, count(*) as sales,
         coalesce(sum(e.commission_amount_cents),0) as commission_cents
  from leads l join enrollments e on e.lead_id = l.id
  where e.status in ('approved','submitted','pending')
  group by 1,2
),
spend as (
  select spend_date as d, campaign_id, sum(spend_amount_cents) as spend_cents
  from ad_spend group by 1,2
)
select
  coalesce(s.d, ld.d, ad.d, sd.d) as d,
  coalesce(s.campaign_id, ld.campaign_id, ad.campaign_id, sd.campaign_id) as campaign_id,
  coalesce(s.spend_cents,0) as spend_cents,
  coalesce(ld.leads,0) as leads,
  coalesce(ad.appts,0) as appts,
  coalesce(sd.sales,0) as sales,
  coalesce(sd.commission_cents,0) as commission_cents,
  case when coalesce(ld.leads,0) > 0 then s.spend_cents::numeric / ld.leads end as cpl_cents,
  case when coalesce(ad.appts,0) > 0 then s.spend_cents::numeric / ad.appts end as cpa_cents,
  case when coalesce(sd.sales,0) > 0 then s.spend_cents::numeric / sd.sales end as cps_cents
from spend s
full outer join leads_daily ld on ld.d = s.d and ld.campaign_id = s.campaign_id
full outer join appts_daily ad on ad.d = s.d and ad.campaign_id = s.campaign_id
full outer join sales_daily sd on sd.d = s.d and sd.campaign_id = s.campaign_id;

-- ----------------------------------------------------------------------------
-- VIEW: v_agent_funnel — agent-level conversion funnel
-- ----------------------------------------------------------------------------
create or replace view v_agent_funnel as
select
  a.id as agent_id,
  a.full_name,
  count(distinct l.id)                                             as leads_assigned,
  count(distinct case when c.outcome in ('connected','appointment_set','sold') then l.id end) as contacted,
  count(distinct case when ap.status in ('scheduled','confirmed','completed') then l.id end) as appointments,
  count(distinct case when e.status in ('approved','submitted','pending') then l.id end)     as sales,
  coalesce(sum(e.commission_amount_cents),0)                       as commission_cents
from agents a
left join leads        l  on l.assigned_agent_id = a.id
left join call_logs    c  on c.lead_id = l.id and c.agent_id = a.id
left join appointments ap on ap.lead_id = l.id and ap.agent_id = a.id
left join enrollments  e  on e.lead_id = l.id and e.agent_id = a.id
group by a.id, a.full_name;

-- ----------------------------------------------------------------------------
-- VIEW: v_compliance_exceptions — anything broken
-- ----------------------------------------------------------------------------
create or replace view v_compliance_exceptions as
select * from compliance_audit_events
where severity in ('error','critical') or result = 'fail'
order by created_at desc;

-- ----------------------------------------------------------------------------
-- FUNCTION: fn_score_lead — weighted lead score (called by workflow 04)
-- inputs: a leads row plus optional intent_score from AI session
-- output: integer 0–100
-- ----------------------------------------------------------------------------
create or replace function fn_score_lead(p_lead_id uuid, p_intent int default null)
returns int language plpgsql as $$
declare
  v_score numeric := 0;
  v_lead leads%rowtype;
  v_age_minutes numeric;
  v_source_weight numeric;
begin
  select * into v_lead from leads where id = p_lead_id;
  if not found then return 0; end if;

  v_age_minutes := extract(epoch from (now() - v_lead.created_at)) / 60;

  -- Recency (max 25): newer = better, decays over 24h
  v_score := v_score + greatest(0, 25 - (v_age_minutes / 60.0));

  -- Intent (max 35) from AI qualification
  if p_intent is null then
    select coalesce(intent_score,0) into p_intent
    from ai_qualification_sessions
    where lead_id = p_lead_id
    order by created_at desc limit 1;
  end if;
  v_score := v_score + (coalesce(p_intent,0) * 0.35);

  -- Medicare status (max 20)
  v_score := v_score + case v_lead.medicare_status
    when 'on_medicare'    then 18
    when 'turning_65'     then 20
    when 'helping_family' then 12
    when 'disability'     then 16
    when 'unsure'         then 8
    else 0 end;

  -- Source quality (max 12)
  v_source_weight := case v_lead.source
    when 'google_search'   then 12
    when 'referral'        then 12
    when 'youtube_organic' then 10
    when 'local_seo'       then 9
    when 'meta_retarget'   then 7
    when 'direct_mail_qr'  then 8
    when 'community_event' then 9
    when 'meta_cold'       then 5
    else 4 end;
  v_score := v_score + v_source_weight;

  -- Geo licensing (max 5): we have an active agent in this state?
  if exists (select 1 from agent_licenses al join agents a on a.id = al.agent_id
              where al.state = v_lead.state and al.active and a.active and al.expires_at > now()) then
    v_score := v_score + 5;
  end if;

  -- Consent strength (max 3): explicit + recent
  if v_lead.consent_valid and v_lead.created_at > now() - interval '7 days' then
    v_score := v_score + 3;
  end if;

  return least(100, greatest(0, round(v_score)::int));
end $$;

-- ----------------------------------------------------------------------------
-- FUNCTION: fn_route_lead — pick best licensed, available agent
-- ----------------------------------------------------------------------------
create or replace function fn_route_lead(p_lead_id uuid)
returns uuid language plpgsql as $$
declare
  v_state char(2);
  v_agent_id uuid;
begin
  select state into v_state from leads where id = p_lead_id;
  if v_state is null then return null; end if;

  -- Pick agent licensed in state, active, with current capacity, round-robin by least-recently-assigned.
  with eligible as (
    select a.id,
           coalesce((select max(assigned_at) from lead_assignments la where la.agent_id = a.id), '1970-01-01'::timestamptz) as last_assigned,
           (select count(*) from lead_assignments la
              where la.agent_id = a.id and la.assigned_at::date = current_date) as today_count
    from agents a
    join agent_licenses al on al.agent_id = a.id
    where a.active and al.active and al.state = v_state and al.expires_at > now()
  )
  select id into v_agent_id
  from eligible
  where today_count < 100  -- safety cap; agents.capacity_per_day is the soft cap
  order by today_count asc, last_assigned asc
  limit 1;

  return v_agent_id;
end $$;

-- ----------------------------------------------------------------------------
-- FUNCTION: fn_propagate_opt_out — single-call opt-out propagation
-- ----------------------------------------------------------------------------
create or replace function fn_propagate_opt_out(
  p_phone text default null,
  p_email text default null,
  p_channel text default 'manual',
  p_reason text default null,
  p_raw text default null
) returns int language plpgsql as $$
declare
  v_count int := 0;
begin
  insert into opt_outs (phone, email, channel, reason, raw_message, processed, processed_at)
  values (p_phone, lower(p_email), p_channel, p_reason, p_raw, true, now());

  update leads l
     set opt_out = true,
         opt_out_at = coalesce(l.opt_out_at, now()),
         status = 'blocked',
         bucket = 'blocked'
   where (p_phone is not null and l.phone = p_phone)
      or (p_email is not null and lower(l.email::text) = lower(p_email));
  get diagnostics v_count = row_count;

  -- Add to suppression list as belt-and-braces
  insert into suppression_list (phone, phone_hash, email, email_hash, reason, source)
  select p_phone,
         case when p_phone is null then null else encode(digest(p_phone,'sha256'),'hex') end,
         lower(p_email),
         case when p_email is null then null else encode(digest(lower(p_email),'sha256'),'hex') end,
         coalesce(p_reason,'opt_out'),
         p_channel
  on conflict do nothing;

  insert into compliance_audit_events (event_type, result, details, source_workflow, severity)
  values ('opt_out_processed','pass',
          jsonb_build_object('phone',p_phone,'email',p_email,'channel',p_channel,'leads_updated',v_count),
          '09-opt-out-suppression','info');

  return v_count;
end $$;

-- ----------------------------------------------------------------------------
-- FUNCTION: fn_dedupe_lead — link near-duplicates
-- ----------------------------------------------------------------------------
create or replace function fn_dedupe_lead(p_lead_id uuid) returns uuid language plpgsql as $$
declare
  v_phone_hash text; v_email_hash text; v_dup uuid;
begin
  select phone_hash, email_hash into v_phone_hash, v_email_hash from leads where id = p_lead_id;

  select id into v_dup from leads
   where id <> p_lead_id
     and duplicate_of is null
     and ((v_phone_hash <> '' and phone_hash = v_phone_hash)
       or (v_email_hash <> '' and email_hash = v_email_hash))
   order by created_at asc
   limit 1;

  if v_dup is not null then
    update leads set duplicate_of = v_dup, status = 'duplicate' where id = p_lead_id;
    insert into compliance_audit_events (lead_id, event_type, result, details, source_workflow)
    values (p_lead_id, 'duplicate_lead_merged','pass', jsonb_build_object('canonical', v_dup),'01-lead-capture');
  end if;
  return v_dup;
end $$;

-- ----------------------------------------------------------------------------
-- FUNCTION: fn_check_tpmo_consent_integrity — multi-TPMO consent must list each
-- receiving entity with individual consent_given booleans.
-- ----------------------------------------------------------------------------
create or replace function fn_check_tpmo_consent_integrity(p_lead_id uuid)
returns boolean language plpgsql as $$
declare
  v_row consent_logs%rowtype;
  v_entities jsonb;
begin
  select * into v_row from consent_logs
   where lead_id = p_lead_id and consent_type = 'multi_tpmo_share'
   order by created_at desc limit 1;

  if not found then return true; end if; -- no multi-TPMO sharing claimed

  v_entities := v_row.consented_entities;
  if v_entities is null or jsonb_typeof(v_entities) <> 'array' then
    insert into compliance_audit_events (lead_id, event_type, result, details, severity, source_workflow)
    values (p_lead_id,'multi_tpmo_consent_mismatch','fail',
            jsonb_build_object('error','no entities array'),'critical','10-daily-compliance-audit');
    return false;
  end if;

  -- every entity must have name + accepted (boolean); accepted must be present per entity
  if exists (
    select 1 from jsonb_array_elements(v_entities) e
    where (e->>'name') is null or (e->>'accepted') is null
  ) then
    insert into compliance_audit_events (lead_id, event_type, result, details, severity, source_workflow)
    values (p_lead_id,'multi_tpmo_consent_mismatch','fail',
            jsonb_build_object('entities',v_entities),'critical','10-daily-compliance-audit');
    return false;
  end if;
  return true;
end $$;
