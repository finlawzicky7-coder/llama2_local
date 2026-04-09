# Phase 1 — Funnel Prioritization

Scored each funnel on demand, speed-to-revenue, competition, margin, and cross-funnel
leverage in the Sacramento / Rocklin market. Scale: 1 (weak) – 5 (strong).

| Funnel | Demand | Speed to $ | Low Competition | Margin | Leverage | Total |
| --- | --- | --- | --- | --- | --- | --- |
| Mid-Term Rentals (Travel Nurses) | 5 | 4 | 5 | 5 | 4 | **23** |
| Cleaning / Turnover Services | 5 | 5 | 3 | 3 | 5 | **21** |
| Airbnb Co-Hosting | 4 | 3 | 2 | 5 | 4 | 18 |
| RV Rentals Lead Gen | 3 | 3 | 4 | 3 | 2 | 15 |

## Why MTR for travel nurses wins

- Sacramento anchors five major hospital systems within 10 miles: UC Davis Medical Center,
  Sutter Medical Center, Kaiser Sacramento, Mercy General, and Shriners. Rocklin serves
  Kaiser Roseville and Sutter Roseville overflow.
- Travel-nurse contracts are 13 weeks, typical stipend $2,800–$4,500/mo for housing.
- A furnished 1-bed commands $2.5–3.5k/mo vs ~$1.8k long-term — ~60% gross margin lift.
- Competition is mostly national platforms (Furnished Finder, Travel Nurse Housing); few
  local operators run dedicated capture funnels.

## Why Cleaning / Turnover is the #2 pick

- Fastest path to cash: one lead → one booking in 48 hours, no inventory.
- Acts as the distribution arm for the other three funnels — cleaners talk to every
  Airbnb host and MTR landlord in the city.
- Existing cleaning clients are the warmest possible leads for Airbnb Co-Hosting and
  MTR placement services later.

## Deferred: Airbnb Co-Hosting

Co-hosting is the highest-margin funnel long-term but requires a portfolio of 3–5
existing properties to credibly sell 20% management fees. We'll re-open this funnel
once cleaning gives us host relationships to convert.

## Deferred: RV Rentals Lead Gen

Lowest score — RV demand in Sacramento is seasonal (April–October), lead fees
cap LTV, and it has weak synergy with the housing-oriented funnels.

## Decision

Build **MTR (Travel Nurses)** and **Cleaning / Turnover** in parallel. Both share the
same lead-capture → Supabase → n8n → Gmail + Stripe pipeline, so shared infra is
amortized across both from day one.
