-- Ringback — Row-Level Security policies (Supabase / Postgres)
-- Apply AFTER `schema.sql`.
--
-- Threat model:
--   - The frontend uses the `anon` and `authenticated` roles.
--   - Server-side workers use the `service_role` (bypasses RLS).
--   - Default posture: DENY for `anon`. Allow only the rows whose
--     `tenant_id` matches the caller's tenant for `authenticated`.
--
-- The convention is that the JWT carries `app_metadata.tenant_id` (uuid),
-- which we read via `auth.jwt() -> 'app_metadata' ->> 'tenant_id'`.
--
-- Platform admins are looked up via `platform_admins.auth_user_id`.

-- helper: current tenant id from JWT
create or replace function app_current_tenant_id()
returns uuid
language sql
stable
as $$
    select nullif(coalesce(
        auth.jwt() -> 'app_metadata' ->> 'tenant_id',
        auth.jwt() ->> 'tenant_id'
    ), '')::uuid
$$;

-- helper: is current auth user a platform admin
create or replace function app_is_platform_admin()
returns boolean
language sql
stable
as $$
    select exists (
        select 1 from platform_admins pa
        where pa.auth_user_id = auth.uid()
    )
$$;

-- ─────────────────────────────────────────────────────────────────────
-- Enable RLS on every tenant-scoped table.
-- ─────────────────────────────────────────────────────────────────────

alter table tenants            enable row level security;
alter table users              enable row level security;
alter table phone_numbers      enable row level security;
alter table business_hours     enable row level security;
alter table service_zips       enable row level security;
alter table job_types          enable row level security;
alter table customers          enable row level security;
alter table calls              enable row level security;
alter table messages           enable row level security;
alter table bookings           enable row level security;
alter table digests            enable row level security;
alter table events             enable row level security;
alter table subscriptions      enable row level security;
alter table usage_records      enable row level security;
alter table platform_admins    enable row level security;

-- ─────────────────────────────────────────────────────────────────────
-- Default deny for anon (no policy = no access once RLS is on).
-- We add explicit policies only for `authenticated` and `platform_admin`.
-- ─────────────────────────────────────────────────────────────────────

-- tenants: a tenant user can read their own row.
drop policy if exists tenants_select_own on tenants;
create policy tenants_select_own on tenants
    for select to authenticated
    using (id = app_current_tenant_id() or app_is_platform_admin());

drop policy if exists tenants_update_own on tenants;
create policy tenants_update_own on tenants
    for update to authenticated
    using (id = app_current_tenant_id())
    with check (id = app_current_tenant_id());

-- users: tenant members see other members of their tenant.
drop policy if exists users_select_own_tenant on users;
create policy users_select_own_tenant on users
    for select to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin());

drop policy if exists users_modify_own_tenant on users;
create policy users_modify_own_tenant on users
    for all to authenticated
    using (tenant_id = app_current_tenant_id())
    with check (tenant_id = app_current_tenant_id());

-- generic helper macro: emit standard CRUD policies for tenant-scoped tables.
-- (Postgres doesn't have macros, so we expand manually below.)

-- phone_numbers
drop policy if exists phone_numbers_tenant_isolated on phone_numbers;
create policy phone_numbers_tenant_isolated on phone_numbers
    for all to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin())
    with check (tenant_id = app_current_tenant_id());

-- business_hours
drop policy if exists business_hours_tenant_isolated on business_hours;
create policy business_hours_tenant_isolated on business_hours
    for all to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin())
    with check (tenant_id = app_current_tenant_id());

-- service_zips
drop policy if exists service_zips_tenant_isolated on service_zips;
create policy service_zips_tenant_isolated on service_zips
    for all to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin())
    with check (tenant_id = app_current_tenant_id());

-- job_types
drop policy if exists job_types_tenant_isolated on job_types;
create policy job_types_tenant_isolated on job_types
    for all to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin())
    with check (tenant_id = app_current_tenant_id());

-- customers
drop policy if exists customers_tenant_isolated on customers;
create policy customers_tenant_isolated on customers
    for all to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin())
    with check (tenant_id = app_current_tenant_id());

-- calls
drop policy if exists calls_tenant_isolated on calls;
create policy calls_tenant_isolated on calls
    for all to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin())
    with check (tenant_id = app_current_tenant_id());

-- messages
drop policy if exists messages_tenant_isolated on messages;
create policy messages_tenant_isolated on messages
    for all to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin())
    with check (tenant_id = app_current_tenant_id());

-- bookings
drop policy if exists bookings_tenant_isolated on bookings;
create policy bookings_tenant_isolated on bookings
    for all to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin())
    with check (tenant_id = app_current_tenant_id());

-- digests
drop policy if exists digests_tenant_isolated on digests;
create policy digests_tenant_isolated on digests
    for select to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin());

-- events: read-only for tenant; only service_role and triggers may insert.
drop policy if exists events_tenant_select on events;
create policy events_tenant_select on events
    for select to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin());

-- subscriptions: read-only for tenant.
drop policy if exists subscriptions_tenant_select on subscriptions;
create policy subscriptions_tenant_select on subscriptions
    for select to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin());

-- usage_records: read-only for tenant.
drop policy if exists usage_records_tenant_select on usage_records;
create policy usage_records_tenant_select on usage_records
    for select to authenticated
    using (tenant_id = app_current_tenant_id() or app_is_platform_admin());

-- platform_admins: only platform admins can read this table.
drop policy if exists platform_admins_self on platform_admins;
create policy platform_admins_self on platform_admins
    for select to authenticated
    using (auth_user_id = auth.uid() or app_is_platform_admin());

-- ─────────────────────────────────────────────────────────────────────
-- Sanity checks (run as a migration test):
--   1. As anon: every select should return zero rows.
--   2. As authenticated with tenant_id A: rows for tenant A only.
--   3. As authenticated with tenant_id B: rows for tenant B only;
--      attempts to insert with tenant_id A must fail the WITH CHECK.
--   4. As service_role: full access.
-- ─────────────────────────────────────────────────────────────────────
