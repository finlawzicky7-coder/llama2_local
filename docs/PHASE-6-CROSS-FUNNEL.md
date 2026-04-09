# Phase 6 — Cross-Funnel Optimization

The two launched funnels are intentionally adjacent. Every cleaning customer is
a candidate MTR/cohosting operator, and every MTR landlord needs a turnover
cleaner. Cross-funnel motion is not a "nice to have" — it's half the ROI.

## Overlap map

```
                  +-------------+
                  |  Cleaning   |
                  +------+------+
                         |
              manages units of
                         |
                         v
   +------------+  rents to  +----------------------+
   | MTR host   +----------->+ Travel nurse tenant  |
   +------+-----+            +----------------------+
          |
     portfolio of 3+
          |
          v
   +------------+
   | Co-hosting |  (Phase 8 re-activation)
   +------------+
```

## Routing rules

| Inbound signal | Primary funnel | Cross-sell trigger |
| --- | --- | --- |
| Cleaning lead w/ 3+ STR units | cleaning | cohosting queue |
| Cleaning lead mentioning "monthly" or "travel nurse" | cleaning | MTR placement service |
| MTR lead who books | mtr | offer mid-stay clean at week 6 |
| MTR lead who doesn't book but has landlord-style language | mtr | cohosting queue |

Stored on `raw_payload.upsell_funnel` at capture time via
`shared/lead-router.js#crossFunnelUpsell()`.

## Weekly cross-funnel review (manual for now)

Every Monday, run this query in Supabase SQL editor:

```sql
select id, name, email, funnel_source, raw_payload->>'upsell_funnel' as upsell,
       lead_score, status, created_at
  from leads
 where raw_payload ? 'upsell_funnel'
   and raw_payload->>'upsell_funnel' is not null
   and status in ('new','contacted','qualified')
 order by lead_score desc
 limit 25;
```

Top 25 cross-funnel candidates → manual outreach from the second funnel's
Gmail, no automation needed until volume justifies it.
