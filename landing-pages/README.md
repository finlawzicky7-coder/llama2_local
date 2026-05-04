# Landing Pages

Three compliant templates:

| File | Use |
|---|---|
| `medicare-review.html` | Evergreen general-funnel page for Google Search + paid social |
| `t65-funnel.html` | Turning-65 / Initial Enrollment Period funnel (year-round) |
| `aep-funnel.html` | Annual Enrollment Period (Oct 15 – Dec 7) funnel |

Plus shared assets: `styles.css`, `consent-tracker.js`.

## Deployment

Recommended host: **Cloudflare Pages** or **Vercel**. Both let you ship a `/api/lead-capture` server function in front of n8n that:

1. Verifies the Cloudflare Turnstile token (via Cloudflare's siteverify endpoint).
2. Adds the **HMAC signature** header (`x-signature`) using `WEBHOOK_HMAC_SECRET`.
3. Forwards to `n8n.your-domain.com/webhook/medicare-lead-capture`.

That keeps the HMAC secret server-side and makes the public form un-spoofable.

## Required template merge tokens

Replace at build/deploy time — never leave `{{...}}` placeholders live:

- `{{AGENCY_NAME}}` — legal name on file with carriers
- `{{LICENSE_NUMBERS}}` — pipe-separated state license numbers
- `{{ADDRESS}}` — physical address
- `{{PHONE}}` — main listed line
- `{{N_CARRIERS}}` — count of carriers represented in this geo
- `{{N_PLANS}}` — count of plans across those carriers
- `{{TURNSTILE_SITE_KEY}}` — Cloudflare Turnstile site key
- `{{CAMPAIGN_ID}}` — Supabase `campaigns.id` for this page

## Compliance review checklist for any new landing page

- [ ] Education first; sales second.
- [ ] **Above the fold:** "Not Medicare. Not affiliated with the federal government."
- [ ] **TPMO disclaimer** visible without scrolling on mobile.
- [ ] No flag-blue / red / white / Medicare-card iconography.
- [ ] No "best plan," "save up to," "free benefits," "free money," "extra benefits," "compare ALL plans."
- [ ] Phone, email, ZIP, state, Medicare status — only what is needed.
- [ ] Birth month/year only behind a `<details>` if collected at all.
- [ ] Consent block lists each receiving entity individually, with separate checkboxes.
- [ ] Recording-notice consent checkbox.
- [ ] Footer carries license numbers, address, full TPMO disclaimer.
- [ ] Privacy policy link, opt-out link, terms link visible.
- [ ] Page passes WCAG 2.2 AA (keyboard, contrast, screen-reader labels).
- [ ] Page is timestamped and snapshotted on each deploy → archived to `consent-evidence` bucket.
