# Stripe Payment Links

Create these in the Stripe Dashboard (`Payments → Payment links → New`) and
paste the resulting URLs into the GitHub repo secrets listed at the bottom.
Each link should carry `client_reference_id=<lead_id>` appended at click time
so Stripe webhooks can reconcile payments to the Supabase `leads` row.

## MTR (Travel Nurses)

| Product | Type | Price | Notes |
| --- | --- | --- | --- |
| Holding deposit | One-time | $500 | Refundable; holds a unit for 72 hours |
| First month rent — 1BR | One-time | $2,850 | Midtown / East Sac tier |
| First month rent — 1BR premium | One-time | $2,950 | Sutter-adjacent |
| First month rent — 2BR | One-time | $3,250 | Rocklin / Kaiser Roseville |
| Monthly rent — 1BR (recurring) | Subscription | $2,850 / mo | Cancel anytime with 30-day notice |
| Monthly rent — 2BR (recurring) | Subscription | $3,250 / mo | Cancel anytime with 30-day notice |

Collect: email, phone, shipping address. Enable: tax disabled, promo codes on.
Redirect after payment → `https://example.com/mtr-travel-nurses/thanks.html`.

## Cleaning / Turnover

| Product | Type | Price | Notes |
| --- | --- | --- | --- |
| Studio turnover | One-time | $65 | Linen swap included |
| 1BR turnover | One-time | $85 | Linen swap included |
| 2BR turnover | One-time | $115 | Linen swap included |
| Deep clean — 1BR | One-time | $175 | 3-hour scope |
| Deep clean — 2BR | One-time | $225 | 4-hour scope |
| Monthly retainer — 4 turns | Subscription | $320 / mo | 4 scheduled turns, overage $75 each |
| Monthly retainer — 8 turns | Subscription | $600 / mo | 8 scheduled turns, overage $70 each |

Redirect after payment → `https://example.com/cleaning-turnover/thanks.html`.

## Webhook → Supabase

Create a Stripe webhook to your n8n endpoint (or a Supabase Edge Function)
listening on:

- `checkout.session.completed`
- `invoice.paid`
- `charge.refunded`

Handler should upsert into `public.payments`:

```sql
insert into public.payments
  (lead_id, stripe_session_id, funnel_source, amount_cents, currency, status)
values
  (:lead_id, :session_id, :funnel_source, :amount, :currency, :status)
on conflict (stripe_session_id) do update
  set status = excluded.status;
```

## Secrets to add in GitHub repo settings

| Secret | Example |
| --- | --- |
| `STRIPE_LINK_MTR_DEPOSIT` | `https://buy.stripe.com/test_XXXX` |
| `STRIPE_LINK_MTR_1BR` | `https://buy.stripe.com/test_XXXX` |
| `STRIPE_LINK_MTR_2BR` | `https://buy.stripe.com/test_XXXX` |
| `STRIPE_LINK_CLEANING_STUDIO` | `https://buy.stripe.com/test_XXXX` |
| `STRIPE_LINK_CLEANING_1BR` | `https://buy.stripe.com/test_XXXX` |
| `STRIPE_LINK_CLEANING_2BR` | `https://buy.stripe.com/test_XXXX` |
| `STRIPE_LINK_CLEANING_RETAINER_4` | `https://buy.stripe.com/test_XXXX` |
| `STRIPE_LINK_CLEANING_RETAINER_8` | `https://buy.stripe.com/test_XXXX` |
| `STRIPE_WEBHOOK_SECRET` | `whsec_XXXX` |

The deploy workflow injects these into the static pages as `window.__STRIPE_*__`
globals so the front-end can read them without a build step.

## A/B pricing notes

- Test MTR holding deposit at $500 vs $250 for 30 days; the lower deposit
  should lift conversion ~15–20% with minimal cancellation risk.
- Test cleaning studio at $65 vs $75 — the higher price barely dents
  conversion and improves margin ~13%.
- Track results in `funnel_events` with `event_type='price_variant'`.
