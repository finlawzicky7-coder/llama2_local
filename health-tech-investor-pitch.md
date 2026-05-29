# AI-Driven Medicare Advantage Navigation Platform
## Health-Tech Investor Pitch Deck — Build Guide & Content Playbook

> **Product thesis:** A consumer-facing and broker-facing AI platform that uses
> **plain-language translation** and **real-time conversational AI** to help
> beneficiaries navigate Medicare Advantage (MA) enrollment, compare plans, and
> resolve coverage questions — while cutting payer/plan administrative cost.
>
> **Audience:** Seed–Series A health-tech investors (digital health VCs,
> payer-aligned strategic funds, govtech/CMS-adjacent investors).
>
> **How to use this document:** Each section gives you (1) the **slide
> objective**, (2) a **slide-by-slide content prompt** you can hand to a
> designer or generative tool, (3) the **CMS RFI hook** that grounds the slide
> in current federal policy signals, (4) **evidence-based ROI benchmarks**, and
> (5) the **regulatory compliance angle** to pre-empt diligence questions.

---

## Table of Contents

1. [Positioning & Narrative Spine](#1-positioning--narrative-spine)
2. [Deck Architecture (14-slide standard)](#2-deck-architecture-14-slide-standard)
3. [Slide-by-Slide Content Prompts](#3-slide-by-slide-content-prompts)
4. [CMS RFI Alignment Map](#4-cms-rfi-alignment-map)
5. [Evidence-Based ROI Benchmarks](#5-evidence-based-roi-benchmarks)
6. [Regulatory Compliance Roadmap](#6-regulatory-compliance-roadmap)
7. [Unique Value Proposition & Market-Readiness Proof](#7-unique-value-proposition--market-readiness-proof)
8. [Appendix: Diligence-Ready Data Room Checklist](#8-appendix-diligence-ready-data-room-checklist)
9. [Sources & How to Refresh Them](#9-sources--how-to-refresh-them)

---

## 1. Positioning & Narrative Spine

Investors fund a *story with proof*, not a feature list. Anchor the whole deck
on one sentence and repeat its logic on every slide:

> **"68M+ Americans are on Medicare, the fastest-growing segment is Medicare
> Advantage, and beneficiaries face a comprehension crisis that costs plans
> billions in avoidable service contacts — we make plan navigation
> conversational and readable at a 6th-grade level, and we have the compliance
> posture to sell into CMS-regulated channels today."**

The three pillars beneath that sentence (use them as a recurring visual motif):

| Pillar | One-liner | Proof artifact to show |
|---|---|---|
| **Comprehension** | Plain-language translation of plan documents (EOC, SB, ANOC) to ≤6th-grade reading level | Before/after readability score (Flesch-Kincaid) |
| **Conversation** | Real-time, multilingual conversational AI for enrollment & plan-navigation Q&A | Live demo / call-deflection metric |
| **Compliance** | HIPAA + CMS marketing-rule + accessibility (Section 508/WCAG) by design | Compliance roadmap slide (Section 6) |

> ⚠️ **Framing discipline:** Never claim the AI gives "advice" or
> "recommendations" in a way that triggers agent/broker licensing or CMS
> marketing-representative rules. Position as *navigation, education, and
> translation* — a decision-support tool, not a sales agent. This single
> distinction de-risks the regulatory story (see Section 6).

---

## 2. Deck Architecture (14-slide standard)

A tight seed/Series-A health-tech deck. Keep to ~14 slides; push detail to the
appendix/data room.

| # | Slide | Purpose | Time on slide |
|---|---|---|---|
| 1 | Title / Vision | Hook + one-sentence thesis | 20s |
| 2 | The Problem | Comprehension crisis in MA | 45s |
| 3 | Why Now | CMS RFI + MA growth + AI inflection | 45s |
| 4 | The Solution | Plain-language + conversational AI | 60s |
| 5 | Product Demo | Show, don't tell | 90s |
| 6 | How It Works | Architecture + safety rails | 45s |
| 7 | Market Size | TAM/SAM/SOM | 45s |
| 8 | Business Model | Who pays, how much | 45s |
| 9 | ROI / Unit Economics | Admin cost reduction proof | 60s |
| 10 | Regulatory & Compliance | De-risk the bet | 60s |
| 11 | Traction & Market Readiness | Evidence we can sell now | 60s |
| 12 | Competitive Landscape | Why us, defensibility | 45s |
| 13 | Team | Why this team wins | 30s |
| 14 | The Ask | Raise, use of funds, milestones | 45s |

---

## 3. Slide-by-Slide Content Prompts

Each prompt is written so you can paste it into a design tool (Gamma, Beautiful.ai,
Figma + a generative plugin) or hand to a designer. Format: **[OBJECTIVE]**,
**[ON-SLIDE COPY]**, **[VISUAL]**, **[SPEAKER NOTE]**.

### Slide 1 — Title / Vision
- **[OBJECTIVE]** Establish category and aspiration in 5 seconds.
- **[ON-SLIDE COPY]** Company name + tagline: *"Medicare, in plain language —
  on demand."* Subhead: *"Conversational AI that helps beneficiaries understand,
  compare, and enroll in Medicare Advantage plans."*
- **[VISUAL]** Single clean device mockup showing a chat bubble translating a
  dense plan clause into a one-line plain answer. Muted healthcare palette
  (deep blue / warm accent), high contrast for accessibility.
- **[SPEAKER NOTE]** Lead with the human moment: a 72-year-old asking "Will my
  plan cover my insulin?" and getting a clear answer in 3 seconds.

### Slide 2 — The Problem
- **[OBJECTIVE]** Make the comprehension crisis visceral and quantified.
- **[ON-SLIDE COPY]** Three stat callouts:
  - *Medicare plan documents are written at a ~11th–13th-grade reading level;
    the average U.S. adult reads at ~8th grade, and most seniors prefer ≤6th.*
  - *Beneficiaries choosing among 40+ MA plans in a typical county experience
    "choice overload" and leave money/benefits on the table.*
  - *Plans field millions of repetitive member-service calls per year on
    "what's covered / how do I" questions.*
- **[VISUAL]** Split screen: a wall of dense EOC text vs. a confused-beneficiary
  illustration. Animate the stats in one at a time.
- **[SPEAKER NOTE]** Tie cost to confusion: every avoidable call, every wrong
  plan pick, every disenrollment is margin destruction for the plan.

### Slide 3 — Why Now
- **[OBJECTIVE]** Show policy + market + tech tailwinds converging.
- **[ON-SLIDE COPY]** Three columns:
  - **Policy:** "CMS is actively soliciting industry input (RFIs) on digital
    tools, plan transparency, prior-authorization streamlining, and beneficiary
    decision support." (See Section 4.)
  - **Market:** "Medicare Advantage now covers roughly half of all Medicare
    beneficiaries and continues to grow with ~10,000 Americans aging into
    Medicare daily."
  - **Tech:** "LLMs crossed the reliability + cost threshold to do safe,
    grounded plain-language translation and voice conversation at scale."
- **[VISUAL]** A "three rivers converging" diagram.
- **[SPEAKER NOTE]** "Why now" is the single most-tested slide by VCs — make the
  CMS RFI the credibility anchor that you are *building toward where the
  regulator is pointing.*

### Slide 4 — The Solution
- **[OBJECTIVE]** Crisp product definition mapped to the two flagship
  capabilities.
- **[ON-SLIDE COPY]**
  - **Plain-language translation:** "Upload or connect any plan document (EOC,
    Summary of Benefits, ANOC, formulary). We render it at ≤6th-grade reading
    level, in the beneficiary's language."
  - **Real-time conversational AI:** "Ask anything — by text or voice — about
    coverage, costs, networks, drugs, and enrollment steps. Grounded in the
    member's actual plan, with citations back to the source document."
- **[VISUAL]** Two-panel product shot; show a citation chip ("Source: 2025 EOC,
  p.42") to telegraph trustworthiness.
- **[SPEAKER NOTE]** Emphasize *grounding/retrieval* — we don't hallucinate
  benefits; every answer is traceable to the plan's official documents.

### Slide 5 — Product Demo
- **[OBJECTIVE]** Earn belief through a real interaction.
- **[ON-SLIDE COPY]** Minimal — let the demo carry it. Caption: *"Live, not a
  mockup."*
- **[VISUAL]** Embedded 60–90s screen recording: (1) beneficiary asks a question
  in Spanish, (2) voice answer in Spanish with on-screen plain-language text,
  (3) a comparison of two plans on a specific drug cost, (4) a citation reveal.
- **[SPEAKER NOTE]** Pre-record as a fallback; never live-demo on conference
  Wi-Fi. Have the deflection metric ready: "this interaction would have been a
  12-minute call."

### Slide 6 — How It Works (Architecture & Safety)
- **[OBJECTIVE]** Show technical credibility + safety rails (diligence loves
  this).
- **[ON-SLIDE COPY]** Pipeline: *Document ingestion → structured extraction →
  retrieval-augmented generation grounded in plan data → guardrails
  (no medical advice, no enrollment steering, PII redaction) → human-escalation
  handoff.*
- **[VISUAL]** Clean left-to-right architecture diagram with a highlighted
  "Compliance & Guardrail Layer" box.
- **[SPEAKER NOTE]** Name the rails: hallucination controls via grounding +
  citation, scope limiter (navigation not advice), audit logging for CMS
  marketing-rule compliance, PHI minimization.

### Slide 7 — Market Size
- **[OBJECTIVE]** Show a large, reachable, expanding market.
- **[ON-SLIDE COPY]**
  - **TAM:** All Medicare beneficiaries (~68M) and the payers, brokers, and
    FMOs that serve them.
  - **SAM:** Medicare Advantage members (~33M+ and growing) + the plans/agencies
    that must educate and retain them.
  - **SOM:** Year 1–3 beachhead — e.g., 3–5 regional MA plans and a broker/FMO
    network covering N members.
- **[VISUAL]** Concentric TAM/SAM/SOM circles with absolute numbers and a growth
  arrow. *Always cite the year and source under each number.*
- **[SPEAKER NOTE]** Bridge market size to *who pays* (next slide) so it doesn't
  feel like vanity TAM.

### Slide 8 — Business Model
- **[OBJECTIVE]** Make revenue concrete and multi-sided.
- **[ON-SLIDE COPY]** Revenue lines:
  - **B2B2C SaaS to MA plans / payers:** PMPM (per-member-per-month) for the
    navigation + member-service-deflection layer.
  - **Broker/FMO seats:** per-seat or per-enrollment for agent-assist during
    AEP/OEP.
  - **Enterprise translation API:** usage-based for plan-document plain-language
    conversion (508/accessibility compliance driver).
- **[VISUAL]** Three-stream funnel into ARR. Show a sample PMPM and a per-seat
  price with "illustrative" label.
- **[SPEAKER NOTE]** Plans buy because deflection + retention + Star Ratings
  (CAHPS member experience) ROI dwarfs the PMPM (see Section 5).

### Slide 9 — ROI / Unit Economics
- **[OBJECTIVE]** Prove the buyer's payback math. (Detail in Section 5.)
- **[ON-SLIDE COPY]** A single payback table: cost-to-serve reduction per
  deflected contact × deflection rate × member base = annual savings vs.
  contract price → payback in < X months.
- **[VISUAL]** A waterfall: "Status-quo admin cost → after deployment."
- **[SPEAKER NOTE]** Use conservative, sourced benchmarks; label assumptions
  explicitly so a CFO can swap their own numbers.

### Slide 10 — Regulatory & Compliance
- **[OBJECTIVE]** Convert "regulatory risk" into "regulatory moat." (Section 6.)
- **[ON-SLIDE COPY]** A maturity roadmap timeline: HIPAA → SOC 2 → CMS marketing
  rule alignment → Section 508/WCAG → state DOI considerations → SOC 2 Type II.
- **[VISUAL]** Horizontal timeline with status chips (Done / In progress /
  Planned).
- **[SPEAKER NOTE]** Frame: "We treat compliance as a go-to-market accelerator —
  it's why a risk-averse payer will sign."

### Slide 11 — Traction & Market Readiness
- **[OBJECTIVE]** Show you can sell *now*, into MA enrollment & navigation.
- **[ON-SLIDE COPY]** Whatever is true, ranked by strength: signed pilots, LOIs,
  design partners (named plans/FMOs if permitted), waitlist, accuracy benchmark
  vs. human baseline, readability-improvement metric, member NPS from pilot.
- **[VISUAL]** Logo strip + a "metrics that matter" band (accuracy %, deflection
  %, languages supported, readability delta).
- **[SPEAKER NOTE]** If pre-revenue, lead with *enterprise pull* (LOIs) and
  *quality proof* (benchmarks) — readiness ≠ revenue yet.

### Slide 12 — Competitive Landscape
- **[OBJECTIVE]** Show why incumbents and generic chatbots lose.
- **[ON-SLIDE COPY]** 2x2 or feature matrix: us vs. (a) plan-finder/comparison
  sites, (b) call-center BPOs, (c) generic LLM chatbots, (d) broker software.
  Our axes: *grounded accuracy* and *compliance-readiness*.
- **[VISUAL]** 2x2 with us in the top-right; feature checklist table beneath.
- **[SPEAKER NOTE]** Defensibility = proprietary plan-document ingestion +
  compliance posture + multilingual voice + payer data integrations.

### Slide 13 — Team
- **[OBJECTIVE]** Convince that *this* team executes in a regulated market.
- **[ON-SLIDE COPY]** Founders with the trifecta: healthcare/payer domain, AI/ML,
  and regulatory/compliance. Add advisors with CMS/MA operating experience.
- **[VISUAL]** Photos + 1-line credibility tags; advisor logos.
- **[SPEAKER NOTE]** For healthcare, "domain + compliance credibility" beats
  generic startup pedigree.

### Slide 14 — The Ask
- **[OBJECTIVE]** Clear raise, clear milestones.
- **[ON-SLIDE COPY]** "Raising $X to reach [N design partners → N paying plans],
  [SOC 2 Type II], [X members served], [$ARR] within 18 months." Use of funds
  pie: engineering, compliance/security, GTM.
- **[VISUAL]** Milestone timeline tied to the next funding round's metrics.
- **[SPEAKER NOTE]** Tie every dollar to a de-risking milestone an A/B investor
  will underwrite.

---

## 4. CMS RFI Alignment Map

> **What an RFI is and why it matters to investors:** CMS periodically issues
> **Requests for Information (RFIs)** to gather public/industry input before
> rulemaking. Citing the *themes* CMS is actively probing signals that your
> product is aligned with where federal policy — and therefore payer budgets —
> is heading. **Always verify the specific current RFI and its comment window
> before the pitch (see Section 9); cite by title + year, never paraphrase a
> docket as a quote.**

Recurring CMS RFI / policy themes you can map your slides to:

| CMS RFI / policy theme | What CMS is probing | Slide(s) to tie it to | Your alignment statement |
|---|---|---|---|
| **Digital tools & interoperability** (e.g., CMS Interoperability and Prior Authorization rules; FHIR/Blue Button APIs) | Patient access to their own data via standardized APIs | 3, 6 | "We consume plan and benefit data through standards-based APIs, future-proofing against interoperability mandates." |
| **Health-system / digital-health RFI on AI** | Safe, transparent AI in care and coverage navigation | 3, 6, 10 | "Our grounding + citation + audit-log architecture answers CMS's transparency and safety concerns directly." |
| **Medicare Advantage marketing & beneficiary protections** | Curbing misleading marketing; ensuring accurate plan info | 4, 6, 10 | "We are navigation/education, not sales steering — built to the marketing-integrity bar CMS is raising." |
| **Health equity & language access** | Reducing disparities; serving LEP (limited-English-proficiency) and disabled beneficiaries | 2, 4, 11 | "Multilingual + ≤6th-grade + 508/WCAG = direct response to CMS health-equity priorities." |
| **Prior authorization / administrative burden** | Reducing avoidable administrative cost and friction | 2, 8, 9 | "We deflect avoidable contacts and clarify coverage up front, reducing administrative burden CMS has flagged." |
| **Star Ratings / CAHPS member experience** | Member experience now weighted heavily in MA quality scoring | 8, 9, 11 | "Better comprehension lifts CAHPS member-experience measures that drive Star bonuses." |

**How to phrase it on stage (safe construction):**
> "CMS has signaled — through its RFIs and rulemaking on [interoperability /
> marketing integrity / health equity / administrative burden] — that it wants
> exactly the capabilities we built. We're not betting against the regulator;
> we're building toward them."

---

## 5. Evidence-Based ROI Benchmarks

> **Discipline:** Present every number as a **sourced, swappable assumption**.
> Investors and payer CFOs trust a transparent model more than a hero number.
> Label ranges as *industry benchmark* vs. *our pilot result*. Refresh figures
> against current sources (Section 9) before each pitch.

### 5.1 The cost drivers you reduce

| Driver | Why it costs money today | How the platform reduces it |
|---|---|---|
| **Member-service call volume** | Live agent calls are the most expensive service channel; a large share are repetitive "is this covered / how do I" questions | Conversational AI deflects/contains a portion of these; the rest arrive pre-contextualized |
| **Avg. handle time (AHT)** | Long calls while agents look up plan details | AI surfaces grounded answers instantly for agent-assist |
| **Mis-enrollment / churn** | Wrong-plan picks → disenrollment, rapid disenrollment penalties, re-acquisition cost | Better plan navigation improves fit and retention |
| **Document accessibility/translation** | Manual translation + 508 remediation of plan docs is slow and costly | Automated plain-language + multilingual rendering |
| **Star Ratings / CAHPS** | Poor member experience lowers Star bonuses (real revenue in MA) | Comprehension lifts experience measures |

### 5.2 Benchmark inputs (illustrative ranges — verify before use)

> The figures below are **illustrative industry-benchmark ranges** to build the
> model's skeleton. **Do not present them as your data.** Pull current figures
> from the sources in Section 9 and from your own pilots.

| Metric | Illustrative benchmark range | Notes |
|---|---|---|
| Cost per live member-service call | ~$5–$12+ per contact | Varies by channel, geography, complexity; self-service/contained costs a fraction of this |
| Self-service / containment cost | Pennies to <$1 per interaction | The core deflection-savings lever |
| Share of calls that are repetitive/navigational | A large minority to majority | Quantify from the buyer's own call-reason taxonomy in discovery |
| Realistic AI containment/deflection rate | Model conservatively (e.g., 20–40% of eligible contacts) | Use a defensible low number on stage |
| Rapid-disenrollment / churn cost | Hundreds of $ per lost member in re-acquisition | Retention upside often exceeds deflection savings |

### 5.3 The payback model (the slide-9 math)

Present this as a transparent formula the CFO can edit live:

```
Annual deflection savings
  = (Eligible contacts / member / yr)
  × (Member base)
  × (Deflection rate)
  × (Cost per contact − Cost per AI interaction)

Annual retention upside
  = (Members retained that would have churned)
  × (Net value of a retained member-year)

Annual accessibility/ops savings
  = (Documents auto-translated/remediated)
  × (Cost per manual remediation avoided)

Total annual value − Annual contract price
  = Net savings  →  Payback period = Contract price / (Total annual value / 12)
```

> **Stage-ready statement:** "Even at a conservative [20–30%] containment rate
> on just the navigational call segment, the deflection savings alone pay back
> our PMPM in under [X] months — before counting retention and Star-rating
> upside."

### 5.4 ROI proof artifacts to bring to diligence
- A populated spreadsheet model with toggleable assumptions.
- Your pilot's measured deflection/containment rate vs. the benchmark.
- Readability delta (e.g., Flesch-Kincaid grade 12.4 → 5.8) on real plan docs.
- Answer-accuracy benchmark vs. a human-expert gold set.
- Member CSAT/NPS from pilot interactions.

---

## 6. Regulatory Compliance Roadmap

> **Purpose:** Turn the scariest diligence topic into a competitive advantage.
> Show a *staged, dated roadmap* with what's done, in progress, and planned.

### 6.1 Compliance pillars

| Pillar | What it covers | Why investors care |
|---|---|---|
| **HIPAA (Privacy + Security)** | PHI handling, BAAs with payers/vendors, encryption, access controls, breach process | Table stakes to touch member data; no payer signs without it |
| **CMS Medicare marketing rules** | Communications vs. marketing distinction; no misleading info; no improper plan steering; required disclaimers | MA-specific; mis-step = enforcement + lost payer trust |
| **Scope discipline (no advice/no steering)** | Tool gives navigation/education, not medical advice or licensed insurance advice | Avoids triggering agent/broker licensing and clinical-device questions |
| **Section 508 / WCAG 2.x AA accessibility** | Usable by beneficiaries with disabilities; required for many gov-adjacent buyers | Equity mandate + expands addressable buyers |
| **SOC 2 (Type I → Type II)** | Security controls attestation for enterprise procurement | Unlocks payer security reviews |
| **Language access (LEP)** | Multilingual support per civil-rights / equity expectations | Equity priority + market expansion |
| **AI governance & transparency** | Grounding, citations, audit logs, human escalation, model-change control, bias monitoring | Answers emerging CMS/federal AI-safety expectations |
| **State DOI considerations** | Whether any function approaches regulated insurance activity | Keeps you on the right side of the advice/sales line |

### 6.2 Phased roadmap (timeline for Slide 10)

| Phase | Milestones | Typical timing |
|---|---|---|
| **Phase 0 — Foundation (now)** | HIPAA program + policies, BAAs, encryption-at-rest/in-transit, PHI minimization, audit logging, guardrails (no advice/no steering), CMS-marketing-rule review of all copy | Pre-/early pilot |
| **Phase 1 — Enterprise-ready** | SOC 2 Type I, WCAG 2.x AA conformance, accessibility VPAT, pen test, incident-response runbook | Before first paid payer contract |
| **Phase 2 — Scale** | SOC 2 Type II, formal AI governance framework + bias/accuracy monitoring, DPIA/risk assessments, state-by-state activity review | During Series A scale-up |
| **Phase 3 — Defensible moat** | Continuous compliance automation, third-party audits, CMS-aligned transparency reporting, certifications relevant to gov/payer procurement | Series A → B |

### 6.3 Guardrail design (what to actually build and show)
- **Grounding + citations:** every answer traces to the member's plan documents.
- **Scope limiter:** refuses medical advice and insurance recommendations;
  redirects to licensed humans where required.
- **No-steering enforcement:** neutral plan comparisons; no preferential ranking
  that could violate marketing rules.
- **PHI minimization & redaction:** collect the least data necessary.
- **Audit trail:** immutable logs of interactions for compliance review.
- **Human-in-the-loop escalation:** seamless handoff to licensed agents/support.
- **Model-change control:** versioned prompts/models with regression testing on
  an accuracy + safety gold set.

> ⚠️ **This is a roadmap, not legal advice.** Engage qualified healthcare
> regulatory counsel and a HIPAA/SOC 2 auditor; verify current CMS rules before
> making compliance claims to investors or customers.

---

## 7. Unique Value Proposition & Market-Readiness Proof

### 7.1 The UVP in one frame
> **"The only Medicare Advantage navigation platform that combines grounded,
> citation-backed plain-language translation with real-time multilingual
> conversational AI — built compliance-first so risk-averse payers can deploy it
> in regulated enrollment and member-service workflows today."**

Decompose into defensible differentiators (use on Slide 12):

| Differentiator | Why it's hard to copy | Buyer-felt benefit |
|---|---|---|
| **Grounded + cited answers** | Requires plan-document ingestion pipeline + retrieval, not just a chatbot | Trust; no hallucinated benefits; auditability |
| **≤6th-grade plain-language engine** | Tuned for senior comprehension + health literacy | Higher comprehension, fewer calls, equity wins |
| **Real-time multilingual voice** | Voice + language + domain accuracy together | Serves LEP & low-vision beneficiaries |
| **Compliance-first architecture** | HIPAA/CMS/508/SOC 2 baked in from day one | Faster payer procurement; lower risk |
| **Payer data integrations** | Standards-based + relationship-built | Stickiness; switching cost |

### 7.2 Demonstrating market readiness for MA enrollment & navigation
Sequence the readiness proof from strongest available evidence:
1. **Regulatory readiness:** HIPAA in place, SOC 2 underway, CMS-marketing-rule
   review complete → "we can legally deploy in MA channels."
2. **Quality readiness:** accuracy benchmark vs. human experts; readability
   delta on real plan docs; safety/guardrail eval results.
3. **Commercial readiness:** signed pilots, design partners, LOIs from
   plans/FMOs; named logos if permitted.
4. **Operational readiness:** integration with plan-document feeds; languages
   supported; uptime/SLA posture; human-escalation workflow live.
5. **Outcome readiness:** pilot deflection rate, member CSAT/NPS, time-to-answer
   vs. call baseline.

### 7.3 The investor takeaway slide line
> "We're not a science project — we're a compliance-ready product with paying/
> piloting payers, measurable comprehension and deflection results, and a market
> that CMS itself is steering toward us."

---

## 8. Appendix: Diligence-Ready Data Room Checklist

- [ ] Cap table & corporate docs
- [ ] Financial model (with the ROI spreadsheet from Section 5)
- [ ] Product roadmap & architecture docs
- [ ] **Compliance evidence:** HIPAA policies, BAAs, SOC 2 report/status, VPAT,
      pen-test summary, AI governance doc
- [ ] **Safety/quality evals:** accuracy gold-set results, hallucination-rate
      tests, readability benchmarks, bias/fairness checks
- [ ] Pilot results & customer references (deflection, CSAT, retention)
- [ ] Contracts/LOIs/design-partner agreements
- [ ] Security architecture & data-flow diagrams (PHI handling)
- [ ] Regulatory memo from healthcare counsel (advice/steering line analysis)
- [ ] Team bios, advisor agreements, key hires plan
- [ ] GTM plan tied to AEP/OEP enrollment calendar

---

## 9. Sources & How to Refresh Them

> **Critical:** This guide intentionally uses **ranges and described benchmarks**
> rather than hard-coded statistics, because Medicare/MA figures, CMS RFIs, and
> Star-Ratings rules change annually. **Before any investor meeting, pull current
> numbers and cite them on-slide with source + year.** Verify against primary
> sources:

| Topic | Where to verify (primary/authoritative) |
|---|---|
| Medicare & MA enrollment totals, growth | CMS.gov enrollment dashboards; KFF (Kaiser Family Foundation) Medicare Advantage briefs |
| Current CMS RFIs & comment windows | Federal Register (federalregister.gov); CMS.gov newsroom & rulemaking pages; Regulations.gov dockets |
| CMS marketing rules for MA/Part D | CMS Medicare Communications and Marketing Guidelines (MCMG); relevant CFR sections |
| Interoperability / prior-auth rules | CMS Interoperability and Prior Authorization Final Rule pages |
| Star Ratings / CAHPS weighting | CMS Part C & D Star Ratings technical notes |
| Health literacy / reading-level data | CDC, AHRQ, and National Assessment of Adult Literacy resources |
| Call-center cost benchmarks | Industry analyst reports (label as illustrative until you have buyer-specific data) |
| Accessibility standards | Section 508 (Section508.gov) and WCAG (W3C) |
| HIPAA | HHS.gov Office for Civil Rights guidance |
| SOC 2 | AICPA Trust Services Criteria |

**Verification protocol before pitching:**
1. Replace every range/benchmark with a current, sourced figure.
2. Confirm the specific CMS RFI you cite is real, current, and quoted by title +
   year.
3. Have healthcare regulatory counsel review compliance claims.
4. Keep an internal "source-of-truth" sheet mapping each slide number to its
   citation.

---

*This document is a build guide and content playbook for an investor pitch. It is
not legal, financial, or regulatory advice. Validate all statistics, regulatory
claims, and compliance steps with primary sources and qualified professionals
before external use.*
