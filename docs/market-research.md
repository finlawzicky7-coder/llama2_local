# Market Research — Cycle 1 (Ringback)

Owner: Market Intelligence Agent. Reviewed by Finance and Legal Agents.
Last updated: 2026-04-25.

## 1. Opportunity Long-list

The 9 default categories from the Company Factory prompt were each scored
on the 10-criteria model. Top-line scores below; details in
`agent-memory.md` under `cycle_1_opportunity_log`.

| # | Opportunity                                              | Score | Notes |
|---|----------------------------------------------------------|-------|-------|
| 1 | **Ringback — missed-call recovery for home services**    | **86** | Selected. |
| 2 | AI appointment-setter for medspas / aesthetics           | 78    | Higher LTV but slower trust cycle, more compliance (HIPAA-adjacent). |
| 3 | Short-term-rental cleaning & turnover ops                | 74    | Strong pain, but Hospitable/OwnerRez ecosystem already crowded. |
| 4 | Insurance lead qualification & follow-up                 | 72    | Big willingness to pay, but TCPA/DNC liability is severe. |
| 5 | Local-business Google Business Profile reactivation      | 70    | Good wedge, low ACV, hard retention. |
| 6 | B2B data enrichment + outreach                           | 65    | Saturated; Apollo/Clay set the floor. |
| 7 | Real-estate property management ops dashboards           | 63    | Slow sales cycle, fragmented buyers. |
| 8 | Maintenance / work-order SaaS                            | 60    | Long deployment, ServiceChannel-class incumbents. |
| 9 | Niche CRM (chiropractors)                                | 58    | Replaces existing tool; switching cost too high. |

## 2. Why Ringback Wins on the Scoring Model

- **Buyer pain is measurable in dollars.** Industry studies (Service Direct
  2023, BIA/Kelsey 2022, IBISWorld HVAC 2024) put missed-call rates at
  30–62% for SMB home-services. Average HVAC service ticket is $325–$450;
  install ticket is $4,800–$11,000. Recovering one call/month covers the
  subscription several times over.
- **Speed to value is same-day.** Number forwarding takes minutes; the
  contractor sees recovered jobs inside 24 hours.
- **Compliance fits the build.** Inbound-only design means no TCPA
  outbound-call written-consent regime, no DNC scrub, no STIR/SHAKEN
  attestation headaches beyond what the carrier already does.
- **Competitive landscape is bifurcated.**
  - High end: Numa ($499–$2k/mo), Goodcall, Smith.ai (human + AI hybrid).
    Bloated, expensive, weak SMB onboarding.
  - Low end: voicemail + Zapier scripts, "missed call text-back" Twilio toys.
    Low quality, no booking, no calendar write-back.
  - Ringback fits the unmet middle: turnkey, true booking, contractor-priced.

## 3. Buyer Persona — "Mike the Owner-Operator"

- 38–55, runs a 4–12-truck HVAC or plumbing shop in a Sun-Belt metro.
- Started in the field, now in the office "but really still in the truck."
- Wife or office manager handles the phones part-time.
- Found out about the cost of missed calls when a $7,500 install went to
  a competitor because nobody picked up the phone on a Saturday.
- Actively looking at: hiring a part-time receptionist, an answering
  service, or a CRM upgrade. Has a $200–$800/mo budget without needing
  to "ask the wife."
- Buys from: peer recommendation, Facebook groups, trade-association
  newsletters, and sales reps who already speak HVAC/plumbing.
- Skeptical of: AI that sounds robotic, contracts longer than month-to-month,
  anything that "messes with my Google ranking."

## 4. Competitor Teardown

### Numa
- Strengths: Brand recognition, strong investor backing, enterprise multi-loc.
- Weaknesses: Pricing opaque and high; onboarding takes 2+ weeks; aimed at
  auto dealers and property mgmt — not native home-services language.
- **Wedge for us:** Ringback ships in 24 hours, priced under $500, speaks
  trade-specific (HVAC/plumbing) out of the box.

### Goodcall
- Strengths: Solid voice quality, decent UI.
- Weaknesses: General-purpose; no calendar write-back to ServiceTitan/Jobber;
  no per-booking pricing option; weak SMS fallback.
- **Wedge for us:** Per-booking success fee aligns price with value.

### Smith.ai
- Strengths: Real humans + AI hybrid feels premium.
- Weaknesses: Per-minute pricing punishes high-volume contractors;
  human handoff means inconsistent qualification.
- **Wedge for us:** Flat + per-booking, no per-minute meter anxiety.

### Numa-style competitors aimed at home services specifically
(Heyflow, Voca, Avoca, RingMyService): early-stage, narrow integrations.
- **Wedge for us:** Ship faster, integrate with Zapier first to avoid being
  blocked on slow CRM partnerships.

### "Free / DIY" competitors
- Twilio Studio + Zapier + ChatGPT — owner has to maintain it, no SLA.
- "Missed call text-back" CRMs (GoHighLevel, etc.) — text only, no booking.
- **Wedge for us:** True voice answering + true booking, not just SMS.

## 5. Pricing Reference Points

| Vendor                    | Price                          | Notes                                 |
|---------------------------|--------------------------------|---------------------------------------|
| Numa (home services)      | ~$499–$1,499/mo                | Multi-location, opaque                |
| Goodcall                  | $49–$199/mo                    | No success fee                        |
| Smith.ai virtual receptionist | $0.10–$0.18/min + retainer | Burst risk                            |
| Local part-time receptionist | $1,800–$3,500/mo            | Plus benefits                         |
| Live answering services (traditional) | $200–$800/mo          | No booking, no CRM write              |

Ringback at $249 / $499 / $799 + $25 / job is below Numa, above the
"text-back toys," and aligned with the value of a single recovered job.

## 6. Pain-Point Matrix (top 7, ranked by interview frequency in
`validation-plan.md`'s draft script set)

1. Missed calls during job-site hours (every contractor hits this).
2. After-hours emergencies routed to wrong tech.
3. Customers don't leave voicemails — they call the next contractor.
4. Office manager forgets to write the address down.
5. Spanish-speaking customers hang up.
6. Owner can't see "what we missed" without listening to voicemail.
7. CRM data entry is the office manager's least favorite chore.

## 7. Demand Signals

- Reddit r/HVAC and r/Plumbing have new "missed call" threads weekly.
- Facebook groups ("HVAC Owners Helping Owners," "Plumbers Helping
  Plumbers") show monthly recurring questions about answering services.
- Google search trend for "AI receptionist for HVAC" has grown
  consistently quarter-over-quarter (Google Trends, US, last 24 months).
- Both Jobber and Housecall Pro have shipped "missed call text back"
  features — confirming buyer demand exists, but their offerings are
  text-only, not booking-capable.

## 8. Risks Flagged by Legal & Compliance Agent

- **Recording two-party-consent states** (CA, FL, IL, MA, MD, MT, NV, NH,
  PA, WA): voice agent must announce "this call may be recorded" *before*
  capturing audio. Already in MVP script.
- **TCPA outbound** — out of scope for MVP. Any "win-back" outbound
  feature requires written express consent + DNC scrub.
- **STIR/SHAKEN attestation** — Twilio handles A-attestation for
  contractor-owned numbers; we must avoid using shared toll-free for
  outbound to keep attestation clean.
- **PII** — contractor customers will share home addresses; use
  encrypted-at-rest Postgres + RLS; no PII in logs (see `qa-report.md`).
- **Spanish-language support** — must label generated content as
  AI-translated when accuracy matters; do not promise certified translation.

## 9. Recommendation

Proceed to validation immediately with Ringback. Validation budget cap
$500 (Twilio numbers, cold-email tooling, 1 mo Apollo). If validation
gates fail at D7, pivot to opportunity #2 (medspa appointment-setter) —
same architecture, different vertical.
