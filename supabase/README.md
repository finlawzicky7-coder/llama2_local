# Supabase

Apply migrations in order:

```
psql "$SUPABASE_DB_URL" -f migrations/0001_init_core.sql
psql "$SUPABASE_DB_URL" -f migrations/0002_indexes.sql
psql "$SUPABASE_DB_URL" -f migrations/0003_rls_policies.sql
psql "$SUPABASE_DB_URL" -f migrations/0004_views_functions.sql
psql "$SUPABASE_DB_URL" -f migrations/0005_storage_and_retention.sql
psql "$SUPABASE_DB_URL" -f migrations/0006_seed.sql
```

Or via the Supabase CLI:

```
supabase db push
```

## Storage buckets to create (Supabase Dashboard → Storage)

- `call-recordings` — private, encryption at rest, lifecycle 10 years
- `consent-evidence` — private, encryption at rest, lifecycle 7 years (or per policy)
- `soa-evidence` — private, encryption at rest, lifecycle 10 years

Set bucket-level policies:

```sql
-- Service role: full access
-- Compliance role: read-only via short-lived signed URLs only
-- Agent role: read only for files attached to their assigned leads via signed URLs
```

## Roles (recommended Postgres roles in Supabase Auth claim shapes)

| JWT `role` | Capability |
|---|---|
| `service_role` | Full read/write — used by n8n only |
| `compliance` | Read-only across all tables; can read recordings via signed URL |
| `agent` | Auth.users record; reads own leads/calls/appointments via RLS |
| `anon` | Public read of `campaigns` only |

## Things to set in Supabase Vault before launch

- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
- `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN`
- `DNC_VENDOR_KEY`
- `WEBHOOK_HMAC_SECRET`
- `CAL_COM_API_KEY`
- `SLACK_WEBHOOK_URL` (for ops alerts)
