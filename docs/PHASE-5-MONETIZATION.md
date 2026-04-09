# Phase 5 — Monetization

Payment stack is Stripe payment links, no custom checkout code. See
`infrastructure/stripe/payment-links.md` for the full product/price list.

## Revenue per lead targets

| Funnel | Avg order value | Conversion target | Rev / lead |
| --- | --- | --- | --- |
| MTR — 1 month + deposit | $3,350 | 15% | **$502** |
| MTR — 3 month assignment | $8,550 | 10% | $855 |
| Cleaning — first turn | $85 | 35% | $30 |
| Cleaning — 4-turn retainer | $320 / mo | 20% | $64 MRR/lead |

A single booked MTR assignment pays for 30+ cleaning leads' worth of ad spend.
This is why MTR is the anchor funnel and cleaning is the distribution engine.

## Pricing tests to run (first 30 days)

1. **MTR deposit** — $500 vs $250 (50/50 split). Track conversion in `funnel_events`
   with `event_type='price_variant'`, `payload: { variant: 'deposit_500' | 'deposit_250' }`.
2. **Cleaning studio** — $65 vs $75. Expect <5% conversion drop at $75, so margin wins.
3. **Cleaning retainer** — monthly vs 3-month prepay (10% discount). Prepay
   dramatically reduces churn; measure after 45 days.

## Upsell paths

- **MTR booked** → offer mid-stay deep clean ($175) at week 6 of contract.
- **Cleaning retainer customer** → if they own 2+ units, pitch Airbnb co-hosting
  (reserved for Phase 8 / funnel re-activation).
- **MTR lead that goes cold** → 60-day re-activation: "New listings opened near
  UC Davis for your next contract".

## Refund / cancellation rules

- MTR holding deposit: refundable up to 72h after checkout.
- Cleaning: cancel up to 24h before scheduled turn for no charge; inside 24h
  charge 50%.
- All refunds trigger the Stripe `charge.refunded` webhook, which flips
  `payments.status='refunded'` and leaves `leads.status` untouched so the
  lead can re-enter a nurture sequence.
