# Ad Account Setup Playbooks

Concrete configuration for the three paid channels you'll use first. Compliance is baked into the configuration, not bolted on.

---

## Google Ads — Search

### 1. Account structure

```
MCC (manager) account
└── Operating account: "your-agency-medicare"
    ├── Campaign: Search — Medicare Review — [STATE]      (one per state)
    │   ├── Ad Group: Generic Medicare Help
    │   ├── Ad Group: Medicare Plan Comparison
    │   ├── Ad Group: T65 Initial Enrollment
    │   └── Ad Group: AEP Annual Enrollment (active Oct 1 – Dec 7)
    └── Campaign: Search — Medicare Supplement — [STATE]  (separate campaign for MS)
```

One state per campaign, not one campaign for "all states." This lets you bid by state, control spend by state, and pause a state cleanly if a license issue arises.

### 2. Keywords

Tight, intent-driven, exact + phrase only. **Do not** use broad match for Medicare keywords — too much spam, too many CMS-prohibited search terms.

**Generic Medicare Help (exact, phrase):**
- `[medicare help]`
- `[talk to medicare agent]`
- `[medicare review]`
- `[medicare options near me]`
- `"licensed medicare agent"`

**Plan Comparison:**
- `"medicare plan comparison"`
- `[compare medicare plans]`
- `[medicare advantage vs supplement]`

**T65:**
- `"turning 65 medicare"`
- `[when do i sign up for medicare]`
- `[medicare initial enrollment period]`

**AEP:**
- `[medicare annual enrollment]`
- `[medicare aep]`
- `[change medicare plan]`

### 3. Negative keyword list (universal — apply to every campaign)

```
free, free benefits, free money, free part b, free part d
best, best plan, best medicare plan
extra benefits, savings, save money, lower premium
medicare.gov, medicare gov, official medicare
fraud, scam, lawsuit, complaint
job, jobs, career, hiring
training, certification, ahip
how to become an agent
```

The first three groups exist because **we do not want to be eligible for searches that imply we're going to deliver those things.** The rest are intent-mismatch.

### 4. Ad copy templates (compliance-reviewed)

**Headline 1:** Talk to a Licensed Medicare Agent
**Headline 2:** Independent Agency • Multi-Carrier
**Headline 3:** Free 15-Minute Review
**Description 1:** Plain-English help comparing Medicare options where you live. We are not Medicare or the federal government.
**Description 2:** No "best plan" pitches. We don't offer every plan in your area — call Medicare.gov or 1-800-MEDICARE for all options.

**Forbidden in ad copy** (will trigger Google's policy review *and* MCMG findings):
- "best," "save up to," "guaranteed," "free benefits," "$0 premium" (without specific qualification)
- "official Medicare," anything implying government affiliation
- Specific carrier names (also disallowed by Google's Medicare ad policy)

### 5. Conversion tracking

- **Lead form submit** — fired by `consent-tracker.js` via `gtag('event', 'lead_submit', {channel:'google_search'})`.
- **Appointment booked** — fired by workflow 08 hitting a server-side conversion endpoint with the lead's `gclid`.
- **Sale (enrollment approved)** — fired by workflow that watches `enrollments.status` transitions; sends to Google Ads Enhanced Conversions API with hashed PII.

Use enhanced conversions, not last-click — too noisy for a 30-90 day Medicare sales cycle.

### 6. Bid strategy

- **First 30 days:** Manual CPC. You don't have enough conversion data for smart bidding.
- **After 100+ enrollments:** Switch to **Maximize Conversions** with a target CPA — set tCPA to 1.5× your current CPS to give the algorithm room.
- **Never use Maximize Clicks.** It optimizes for wrong outcome.

### 7. Compliance settings inside Google Ads

- Disable **partner network** (low quality, hard to vet).
- Disable **search partners** for the first 60 days.
- Enable **Medicare advertiser certification** in your account if Google requires it for your geography.
- Set **demographic exclusions** as Google policy requires.
- Add legal-name + agency-address to ad-account verification so all ads display "Paid for by [your-agency]."

---

## Meta Ads (Facebook + Instagram)

### Posture: retargeting only, in year 1

Cold Medicare prospecting on Meta is fraught — audience targeting limitations, beneficiary segments, and a high rate of low-quality clicks. We use Meta only for **retargeting an educated audience** who already engaged with your site or YouTube.

### 1. Pixel + CAPI setup

- Install Meta Pixel on every landing page.
- Configure **server-side Conversions API** (CAPI) via the n8n side: when a lead is captured, fire a CAPI event with hashed email/phone (PII safe handling per Meta's requirements).
- Map events: `Lead` (form submit), `Schedule` (appointment booked), `Purchase` (enrollment approved — value = expected commission).

### 2. Audiences

**Custom audiences:**
- Website visitors who reached the form and didn't submit (last 30 days).
- Video viewers (YouTube + Meta video) who watched ≥ 50%.
- Email-engaged from Postmark (export CSV; upload as hashed list).

**Excluded audiences (always):**
- Existing clients (uploaded CSV from `enrollments`).
- Opted-out leads (uploaded CSV from `opt_outs`).
- Agency staff + anyone in your CRM tagged as "do not market."

**Lookalike audiences:** create a 1% lookalike of your enrollment-completed list. Year 2 territory.

### 3. Creative rules

- All ad copy carries a TPMO-equivalent disclosure ("Independent agency. Not Medicare. Don't offer every plan in your area.")
- No "free" or "savings" claims.
- No carrier logos or plan-specific imagery.
- Education-first: video walkthroughs of how Medicare parts fit together.

### 4. Special-Ad-Category compliance

Insurance ads on Meta typically fall under **Special Ad Categories**, which restricts age/gender/zip targeting. Comply with the framework — do not try to circumvent. Targeting is broad geographic + interest-based.

---

## YouTube — owned channel + YouTube Ads

### 1. Channel posture

- Channel name: **`[Your Agency] Medicare Education`** (clearly your brand, not a Medicare-sounding handle).
- Channel description includes the TPMO disclaimer in full.
- Every video description includes the TPMO disclaimer in the first paragraph.
- Every video has on-screen text "Not Medicare • Not the Federal Government" for the entire duration (lower-third bug).
- Every video opens with a 15-second verbal disclaimer.

### 2. Content cadence

- 1 evergreen education video / week.
- 1 AEP-themed video / week during Sep 15 – Dec 7.
- 1 T65 birthday-month video / quarter.
- Topics are plan-neutral: how parts fit together, what to look for in your ANOC letter, how to compare plans (process, not specific plans), what SHIP is.

### 3. YouTube Ads (TrueView in-stream)

- Targeting: education-first, not retargeting at this stage.
- Custom intent audiences built from search queries: "medicare basics," "turning 65 medicare," "medicare advantage vs supplement."
- Skippable ads only — never use non-skippable for Medicare; high abandonment + poor brand sentiment.
- 30-second cap; first 5 seconds open with the disclaimer.

### 4. Comments + community

- Comments **must be moderated**. Configure YouTube to hold all comments containing keywords like "scam," "fraud," "lawsuit," "complaint," "carrier name," "plan name" for review.
- Never respond to plan-specific questions in comments — direct to a 1:1 review.

---

## Direct Mail (T65 only, year 1)

### 1. Targeting

- Use a list-broker for T65 prospects (people 64.5–65.0) in your launch states. Verify the broker provides **prior express consent or relies on first-party data** — direct mail itself doesn't require TCPA consent, but if the QR-coded landing page submission later triggers SMS/calls, the *form's* consent is what authorizes that.

### 2. Postcard design

- Front: "Turning 65? Talk to a licensed Medicare agent." + your agency name + a QR code.
- Back: TPMO disclaimer in 10pt minimum, agency address + license numbers, opt-out instructions ("To stop receiving mail from us, write to: [PO Box]").
- **No flag-blue + red + white** (Medicare-card colors). Use earth tones / your brand palette.
- **No fake "official documents"** — no envelope mockups, no "Time-Sensitive Important Information."

### 3. Tracking

- Each batch gets a unique `campaign_id` and `utm_campaign`.
- The QR code goes to `t65-funnel.html` with UTMs prefilled.
- Mail-house reports number sent / delivered → load into `ad_spend` weekly.

---

## Cross-channel rules

- Every channel funnels to a **state-specific landing page**. Don't strip the geography because one of your states isn't covered by an active agent — the routing engine will move that lead to nurture, but the form will still capture honestly.
- Every channel has its own `campaigns` row and `source` label so workflow 11 can compare CPS / opt-out / close-rate by source.
- Every channel's creative is reviewed by compliance before launch and after any material change.
- Every channel has a kill switch (`campaigns.active = false`) you can flip in 5 seconds.
