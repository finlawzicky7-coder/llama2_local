# Phase 8 — Continuous Improvement Loop

Weekly cadence. The goal is to scale winners, kill dead experiments, and
launch the next funnel once the current two clear the MRR thresholds below.

## Weekly metrics review (Monday, 30 min)

Run the following in Supabase and paste into the weekly review doc.

```sql
-- Leads per funnel, last 7 days
select funnel_source, count(*) as leads, avg(lead_score)::int as avg_score
  from leads
 where created_at >= now() - interval '7 days'
 group by 1;

-- Funnel conversion: lead -> paid, last 30 days
select l.funnel_source,
       count(*) filter (where l.status='new')         as open_leads,
       count(*) filter (where l.status='contacted')   as contacted,
       count(*) filter (where l.status='booked')      as booked,
       count(*) filter (where l.status='paid')        as paid,
       round(100.0 * count(*) filter (where l.status='paid')::numeric
             / nullif(count(*),0), 1)                 as conv_pct
  from leads l
 where l.created_at >= now() - interval '30 days'
 group by 1
 order by conv_pct desc nulls last;

-- Revenue per funnel, last 30 days
select funnel_source, sum(amount_cents)/100.0 as revenue_usd, count(*) as txns
  from payments
 where status = 'succeeded'
   and created_at >= now() - interval '30 days'
 group by 1;
```

## Scaling triggers

| Funnel | "Working" threshold | Scale action |
| --- | --- | --- |
| MTR | ≥ 2 bookings / month OR 10 warm leads / week | Add 2nd unit, double SEO posts, start $15/day Meta test |
| Cleaning | ≥ 8 turns / week OR 1 retainer signed | Hire 2nd cleaner, pitch 5 more PMs |

## Kill triggers

| Funnel | "Dead" threshold | Kill action |
| --- | --- | --- |
| MTR | < 3 leads / week for 3 weeks running | Pause ads, re-write hero copy, try paid Furnished Finder promotion |
| Cleaning | < 2 bookings / month | Pause GBP boosts, run pricing A/B, switch to PM-only strategy |

## Next-funnel launch triggers

Open the next funnel (Co-hosting) as soon as BOTH of:
1. Cleaning has ≥ 3 active retainer customers.
2. MTR has ≥ 2 repeat landlord referrers.

Those relationships ARE the co-hosting funnel's initial inventory. Without
them, co-hosting is a cold start.

## Experiments queue

Maintain a ranked list in this file (append below). Each week, promote the
top 1–2 into execution. Never run more than 3 experiments simultaneously
per funnel or attribution breaks.

### Current experiments
- [ ] MTR — test $250 vs $500 holding deposit
- [ ] Cleaning — photo-report vs no-report on review rate
- [ ] MTR — add "pet-friendly" filter to hero (Sacramento skews high pet-owner)
- [ ] Cleaning — bundle laundry pickup as add-on; measure attach rate
