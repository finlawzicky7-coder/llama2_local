# Email Cadence

Six email templates referenced from workflow 07 by `TemplateAlias`. All emails:

- Carry the **TPMO disclaimer** in the footer.
- Carry a **one-click unsubscribe** link (List-Unsubscribe header + URL).
- Are sent from a **monitored marketing domain** with SPF/DKIM/DMARC aligned (`p=reject`).
- Use a clearly-non-government from name (e.g., "Riley at {AGENCY_NAME}", not "Medicare Updates").

## `speed_to_lead_email_v1` — minutes after submission

**Subject:** Quick note about your Medicare review request

> Hi {first_name},
>
> I'm Riley with {AGENCY_NAME} — a licensed insurance agent. I just got your request to review your Medicare options. I tried calling and left a quick message.
>
> A 15-minute call is the easiest way to do this. You can pick a time here: {scheduling_link}.
>
> Quick note: we're not Medicare or the federal government. We don't offer every plan in your area. We currently represent multiple carriers and you can also call Medicare.gov, 1-800-MEDICARE, or your local SHIP for all your options.
>
> Talk soon,
> Riley · Licensed Agent · {AGENCY_NAME}
> {PHONE}

## `day1_followup_v1` — next morning

**Subject:** Still happy to walk you through Medicare when convenient

> Hi {first_name},
>
> Following up — I have a few openings this week if a quick review would help: {scheduling_link}.
>
> No pressure at all. If you'd rather have a 1-page basics guide instead, just hit reply with the word **GUIDE** and I'll send it.
>
> Riley · Licensed Agent · {AGENCY_NAME}

## `day7_education_v1` — value-first

**Subject:** A clear 5-minute primer on how Medicare actually works

> Hi {first_name},
>
> Whether or not we end up talking, here's a plain-English overview of how Medicare's parts fit together — written by a licensed agent and reviewed by our compliance team.
>
> [LINK to PDF on your domain — content must be plan-neutral]
>
> Reach out anytime if you'd like to chat: {scheduling_link}.
>
> Riley · Licensed Agent · {AGENCY_NAME}

## `day14_lastcall_v1` — graceful exit

**Subject:** Closing your file — wanted to give you a last look

> Hi {first_name},
>
> I'll be closing out your request at the end of this week. If you'd still like a quick walk-through, just reply or pick a time: {scheduling_link}. If not, no worries at all — and thanks for considering us.
>
> Riley · Licensed Agent · {AGENCY_NAME}

## `appt_confirmation_v1` — sent on booking

**Subject:** Confirmed — your Medicare review on {appointment_time}

> Hi {first_name},
>
> You're confirmed for **{appointment_time}** with {agent_name}, your licensed agent.
>
> **Before we talk:** please sign your Scope of Appointment here: {soa_url}. It's a CMS form that says we agreed to discuss specific Medicare products. We can't talk about plan-specific details until it's signed.
>
> Quick reminder: we're not Medicare or the federal government. The call will be recorded for compliance.
>
> See you then,
> {AGENCY_NAME}

## `monthly_evergreen` — long-tail education

**Subject:** What changes in Medicare this fall (heads up before AEP)

> Hi {first_name},
>
> Annual Enrollment runs Oct 15 – Dec 7. Plans change every year and so might your prescriptions and doctors. Here's what to look for:
>
> 1. Your Annual Notice of Change (ANOC) letter from your current plan.
> 2. Whether your prescriptions stayed on the same tier.
> 3. Whether your doctors are still in-network.
>
> If you'd like a 15-minute review, here's my calendar: {scheduling_link}.
>
> Riley · Licensed Agent · {AGENCY_NAME}

---

## Footer (every email)

```
{AGENCY_NAME} · License #{LICENSE_NUMBERS} · {ADDRESS} · {PHONE}

We do not offer every plan available in your area. Currently we represent
{N_CARRIERS} organizations which offer {N_PLANS} products in your area.
Please contact Medicare.gov, 1-800-MEDICARE, or your local SHIP to get
information on all of your options.

You're receiving this because you requested a Medicare review at
{landing_page_url}. To stop receiving these messages,
{unsubscribe_url|click here to unsubscribe}.
```

## Headers (every email)

```
List-Unsubscribe: <mailto:unsubscribe@your-domain.com>, <{unsubscribe_url}>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
Auto-Submitted: auto-generated
Precedence: bulk
```
