-- Multi-funnel lead capture schema
-- Run in Supabase SQL editor on a fresh project.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- leads: unified capture for every funnel
-- ---------------------------------------------------------------------------
create table if not exists public.leads (
  id               uuid primary key default gen_random_uuid(),
  name             text not null,
  email            text not null,
  phone            text,
  service_interest text not null,
  city             text,
  budget_or_revenue numeric,
  lead_score       int  not null default 0,
  funnel_source    text not null
    check (funnel_source in ('mtr','cleaning','cohosting','rv')),
  status           text not null default 'new'
    check (status in ('new','contacted','qualified','booked','paid','lost')),
  notes            text,
  raw_payload      jsonb,
  utm_source       text,
  utm_medium       text,
  utm_campaign     text,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

create index if not exists leads_funnel_idx  on public.leads (funnel_source, created_at desc);
create index if not exists leads_status_idx  on public.leads (status);
create index if not exists leads_score_idx   on public.leads (lead_score desc);
create unique index if not exists leads_email_funnel_uk
  on public.leads (lower(email), funnel_source);

-- auto-update updated_at
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

drop trigger if exists trg_leads_touch on public.leads;
create trigger trg_leads_touch
  before update on public.leads
  for each row execute function public.touch_updated_at();

-- ---------------------------------------------------------------------------
-- funnel_events: analytics + attribution
-- ---------------------------------------------------------------------------
create table if not exists public.funnel_events (
  id           bigserial primary key,
  lead_id      uuid references public.leads(id) on delete cascade,
  funnel_source text not null,
  event_type   text not null,   -- view, form_submit, email_open, booked, paid
  payload      jsonb,
  created_at   timestamptz not null default now()
);

create index if not exists funnel_events_lead_idx on public.funnel_events (lead_id);
create index if not exists funnel_events_type_idx on public.funnel_events (funnel_source, event_type, created_at desc);

-- ---------------------------------------------------------------------------
-- payments: shadow copy of Stripe payments for quick reporting
-- ---------------------------------------------------------------------------
create table if not exists public.payments (
  id                 bigserial primary key,
  lead_id            uuid references public.leads(id) on delete set null,
  stripe_session_id  text unique,
  funnel_source      text not null,
  amount_cents       int not null,
  currency           text not null default 'usd',
  status             text not null,   -- pending, succeeded, refunded, failed
  created_at         timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- RLS: anon role can insert leads, only service_role can read/update
-- ---------------------------------------------------------------------------
alter table public.leads         enable row level security;
alter table public.funnel_events enable row level security;
alter table public.payments      enable row level security;

drop policy if exists "anon can insert leads" on public.leads;
create policy "anon can insert leads"
  on public.leads for insert
  to anon
  with check (true);

drop policy if exists "anon can insert events" on public.funnel_events;
create policy "anon can insert events"
  on public.funnel_events for insert
  to anon
  with check (true);

-- service_role bypasses RLS automatically; no read policies for anon by design.
