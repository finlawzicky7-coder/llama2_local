# n8n Workflows

Two workflows, both keyed off Supabase as the source of truth.

## 1. `new-lead-workflow.json` — webhook → email → Slack alert

**Trigger:** Supabase Database Webhook on `public.leads` INSERT, POSTing to
`https://<your-n8n>/webhook/new-lead`.

**Flow:**
1. Webhook receives the lead row.
2. `Shape + Branch` computes `is_hot`/`is_warm` from `lead_score` and picks a
   subject line per funnel.
3. Routes by `funnel_source` (`mtr` vs `cleaning`) to the matching Gmail intro
   template.
4. If the lead is hot (score ≥ 70), pings the `#leads-hot` Slack channel.
5. Logs `intro_email_sent` to `public.funnel_events`.

**Setup:**
- Create Gmail OAuth credential(s): `Gmail MTR`, `Gmail Cleaning`.
- Create Slack API credential: `Slack Bot`, scope `chat:write`.
- Set n8n env vars: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`.
- In Supabase → Database → Webhooks: add a trigger on `public.leads` INSERT
  pointing at your n8n webhook URL.

## 2. `follow-up-sequence.json` — scheduled 3-touch sequence

**Trigger:** hourly cron.

**Flow:**
1. Pulls leads with `status = 'new'`.
2. Computes which follow-up touch is due (day 1 / 3 / 5).
3. Renders the funnel-specific template with `{{name}}` / `{{city}}` vars.
4. Sends via Gmail and logs `followup_dayN` to `public.funnel_events`.

**To stop follow-ups:** update a lead's `status` column to anything other than
`new` (e.g. `contacted`, `booked`, `lost`). The query filter in `Fetch Open
Leads` excludes them automatically.

## Import

```bash
# In n8n:
# Workflows → Import from File → pick new-lead-workflow.json, repeat for follow-up-sequence.json
# Then: open each workflow → update credentials → Activate.
```
