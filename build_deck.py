#!/usr/bin/env python3
"""
Generate a downloadable, editable PowerPoint investor pitch deck for an
AI-driven Medicare Advantage navigation platform.

Output: medicare-advantage-investor-pitch.pptx (16:9)

Run: python3 build_deck.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------------- palette
NAVY      = RGBColor(0x0B, 0x2A, 0x4A)   # deep blue
BLUE      = RGBColor(0x1B, 0x6E, 0xC2)   # accent blue
TEAL      = RGBColor(0x14, 0xA3, 0x8B)   # supporting teal
AMBER     = RGBColor(0xF2, 0x9F, 0x05)   # warm accent
INK       = RGBColor(0x1A, 0x1A, 0x1A)   # body text
SLATE     = RGBColor(0x5B, 0x6B, 0x7B)   # secondary text
LIGHT     = RGBColor(0xF4, 0xF7, 0xFA)   # light fill
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
ROW_ALT   = RGBColor(0xEA, 0xF1, 0xF8)

FONT = "Calibri"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------- helpers
def slide():
    return prs.slides.add_slide(BLANK)


def rect(s, x, y, w, h, color, line=None):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(1)
    shp.shadow.inherit = False
    return shp


def textbox(s, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    return tb, tf


def setpara(p, text, size, color, bold=False, align=PP_ALIGN.LEFT,
            space_after=6, italic=False, font=FONT):
    p.text = text if text else " "
    p.alignment = align
    p.space_after = Pt(space_after)
    r = p.runs[0]
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font
    return p


def add_para(tf, text, size, color, bold=False, align=PP_ALIGN.LEFT,
             space_after=6, italic=False, bullet=False, level=0):
    p = tf.add_paragraph()
    p.level = level
    setpara(p, ("• " + text) if bullet else text, size, color, bold,
            align, space_after, italic)
    return p


def header(s, kicker, title, num):
    """Standard content-slide header with side accent bar."""
    rect(s, 0, 0, Inches(0.28), SH, BLUE)
    tb, tf = textbox(s, Inches(0.6), Inches(0.35), Inches(11.8), Inches(1.3))
    setpara(tf.paragraphs[0], kicker, 13, TEAL, bold=True, space_after=2)
    add_para(tf, title, 30, NAVY, bold=True, space_after=0)
    # slide number
    nb, nf = textbox(s, Inches(12.4), Inches(6.95), Inches(0.8), Inches(0.4))
    setpara(nf.paragraphs[0], str(num), 11, SLATE, align=PP_ALIGN.RIGHT)
    # footer brand
    fb, ff = textbox(s, Inches(0.6), Inches(6.95), Inches(8), Inches(0.4))
    setpara(ff.paragraphs[0], "ClariCare  ·  Medicare, in plain language",
            10, SLATE)


def table(s, rows, cols, x, y, w, h, data, header_fill=NAVY,
          col_widths=None, font_size=12, header_size=12):
    gt = s.shapes.add_table(rows, cols, x, y, w, h).table
    if col_widths:
        for i, cw in enumerate(col_widths):
            gt.columns[i].width = cw
    for r in range(rows):
        for c in range(cols):
            cell = gt.cell(r, c)
            cell.margin_left = Inches(0.1)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            para = tf.paragraphs[0]
            txt = data[r][c]
            is_head = (r == 0)
            setpara(para, txt,
                    header_size if is_head else font_size,
                    WHITE if is_head else INK,
                    bold=is_head, space_after=0)
            if is_head:
                cell.fill.solid(); cell.fill.fore_color.rgb = header_fill
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = ROW_ALT if r % 2 else WHITE
    return gt


def card(s, x, y, w, h, title, body_lines, accent=BLUE, title_size=16):
    rect(s, x, y, w, h, LIGHT)
    rect(s, x, y, w, Inches(0.12), accent)
    tb, tf = textbox(s, x + Inches(0.2), y + Inches(0.28),
                     w - Inches(0.4), h - Inches(0.4))
    setpara(tf.paragraphs[0], title, title_size, NAVY, bold=True, space_after=6)
    for ln in body_lines:
        add_para(tf, ln, 12.5, INK, space_after=5)
    return tb


# ================================================================ SLIDE 1
s = slide()
rect(s, 0, 0, SW, SH, NAVY)
rect(s, 0, Inches(5.0), SW, Inches(0.10), AMBER)
tb, tf = textbox(s, Inches(0.9), Inches(1.5), Inches(11.5), Inches(3.2))
setpara(tf.paragraphs[0], "ClariCare", 60, WHITE, bold=True, space_after=4)
add_para(tf, "Medicare, in plain language — on demand.", 28, AMBER,
         bold=True, space_after=18)
add_para(tf, "Conversational AI that helps beneficiaries understand, compare,",
         20, WHITE, space_after=2)
add_para(tf, "and enroll in Medicare Advantage plans.", 20, WHITE,
         space_after=0)
tb2, tf2 = textbox(s, Inches(0.9), Inches(6.4), Inches(11.5), Inches(0.8))
setpara(tf2.paragraphs[0],
        "Seed / Series A  ·  Health-Tech Investor Pitch  ·  Confidential",
        14, RGBColor(0xC9, 0xD8, 0xE8))

# ================================================================ SLIDE 2  Problem
s = slide()
header(s, "THE PROBLEM", "A comprehension crisis is costing plans billions", 2)
cw = Inches(3.85)
gap = Inches(0.25)
x0 = Inches(0.6)
y0 = Inches(2.0)
ch = Inches(3.7)
card(s, x0, y0, cw, ch, "Documents nobody can read",
     ["Plan documents (EOC, SB, ANOC) are written at an ~11th–13th-grade level.",
      "The average U.S. adult reads at ~8th grade; most seniors prefer ≤6th.",
      "Result: beneficiaries can't tell what's actually covered."], BLUE)
card(s, x0 + cw + gap, y0, cw, ch, "Choice overload",
     ["A typical county offers 40+ Medicare Advantage plans.",
      "Overwhelmed beneficiaries pick on price alone — and leave benefits and money on the table.",
      "Poor fit drives rapid disenrollment and churn."], TEAL)
card(s, x0 + 2 * (cw + gap), y0, cw, ch, "Expensive confusion",
     ["Plans field millions of repetitive 'is this covered / how do I' calls a year.",
      "Live agent contacts are the costliest service channel.",
      "Confusion erodes CAHPS member-experience scores that drive Star bonuses."], AMBER)
tb, tf = textbox(s, Inches(0.6), Inches(5.95), Inches(12), Inches(0.8))
setpara(tf.paragraphs[0],
        "Every avoidable call, every wrong-plan pick, every disenrollment is margin destruction for the plan.",
        15, NAVY, bold=True, italic=True)

# ================================================================ SLIDE 3  Why Now
s = slide()
header(s, "WHY NOW", "Policy, market, and technology are converging", 3)
cw = Inches(3.85); x0 = Inches(0.6); y0 = Inches(2.0); ch = Inches(3.9)
card(s, x0, y0, cw, ch, "Policy tailwind",
     ["CMS is actively soliciting industry input (RFIs) and issuing rules on:",
      "– digital tools & interoperability",
      "– Medicare Advantage marketing integrity",
      "– health equity & language access",
      "– reducing administrative burden.",
      "We build toward where the regulator is pointing."], BLUE)
card(s, x0 + cw + gap, y0, cw, ch, "Market tailwind",
     ["Medicare Advantage now covers roughly half of all Medicare beneficiaries.",
      "~10,000 Americans age into Medicare every day.",
      "Plans compete fiercely on member experience and retention."], TEAL)
card(s, x0 + 2 * (cw + gap), y0, cw, ch, "Technology tailwind",
     ["LLMs crossed the reliability + cost threshold for safe, grounded use.",
      "Plain-language translation and real-time voice are now production-ready.",
      "Retrieval + citations make answers auditable."], AMBER)

# ================================================================ SLIDE 4  Solution
s = slide()
header(s, "THE SOLUTION", "Two capabilities, grounded in the member's real plan", 4)
cw = Inches(5.85); x0 = Inches(0.6); y0 = Inches(2.0); ch = Inches(4.3)
card(s, x0, y0, cw, ch, "1 · Plain-language translation",
     ["Connect any plan document — EOC, Summary of Benefits, ANOC, formulary.",
      "We render it at a ≤6th-grade reading level, in the beneficiary's language.",
      "Readability that turns 12th-grade legalese into a clear, scannable answer.",
      "Drives Section 508 / accessibility compliance automatically."], BLUE, 18)
card(s, x0 + cw + gap, y0, cw, ch, "2 · Real-time conversational AI",
     ["Ask anything — by text or voice — about coverage, costs, networks, drugs, enrollment steps.",
      "Grounded in the member's actual plan, with citations to the source document.",
      "Multilingual; works for low-vision and limited-English beneficiaries.",
      "We don't hallucinate benefits — every answer is traceable."], TEAL, 18)

# ================================================================ SLIDE 5  Demo
s = slide()
header(s, "PRODUCT DEMO", "Live, not a mockup", 5)
rect(s, Inches(0.6), Inches(1.9), Inches(7.2), Inches(4.6), NAVY)
tb, tf = textbox(s, Inches(0.95), Inches(2.2), Inches(6.6), Inches(4.0))
setpara(tf.paragraphs[0], "“¿Mi plan cubre mi insulina?”", 20, AMBER, bold=True, space_after=10)
add_para(tf, "AI (voice + text, Spanish):", 13, RGBColor(0xC9,0xD8,0xE8), bold=True, space_after=4)
add_para(tf, "“Sí. Su plan cubre la insulina como medicamento de Nivel 3. "
             "Paga $35 por un suministro de 30 días en farmacias de la red.”",
         15, WHITE, space_after=10)
add_para(tf, "📎 Fuente: 2025 Evidence of Coverage, p. 42",
         12, TEAL, italic=True, space_after=14)
add_para(tf, "▸ Compares two plans on the same drug cost", 13, WHITE, space_after=4)
add_para(tf, "▸ One tap to reveal the source citation", 13, WHITE, space_after=4)
add_para(tf, "▸ Hands off to a licensed agent when needed", 13, WHITE, space_after=0)
card(s, Inches(8.1), Inches(1.9), Inches(4.6), Inches(4.6),
     "What the demo proves",
     ["Answers are accurate and grounded.",
      "Voice + multilingual works in real time.",
      "Citations build beneficiary and payer trust.",
      "This interaction replaces a ~12-minute live call.",
      "",
      "Tip: pre-record the demo — never rely on conference Wi-Fi."], AMBER, 16)

# ================================================================ SLIDE 6  How it works
s = slide()
header(s, "HOW IT WORKS", "Architecture built for accuracy and compliance", 6)
steps = ["Document\ningestion", "Structured\nextraction",
         "Retrieval-augmented\ngeneration (grounded)", "Guardrail &\ncompliance layer",
         "Member answer\n+ citation"]
n = len(steps)
bw = Inches(2.18); bh = Inches(1.5); gap2 = Inches(0.24)
x = Inches(0.6); y = Inches(2.3)
for i, st in enumerate(steps):
    color = AMBER if i == 3 else BLUE
    r = rect(s, x, y, bw, bh, color)
    tf = r.text_frame; tf.word_wrap = True
    setpara(tf.paragraphs[0], st, 13, WHITE, bold=True, align=PP_ALIGN.CENTER)
    if i < n - 1:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                                x + bw, y + Inches(0.55), gap2, Inches(0.4))
        ar.fill.solid(); ar.fill.fore_color.rgb = SLATE
        ar.line.fill.background(); ar.shadow.inherit = False
    x = x + bw + gap2
card(s, Inches(0.6), Inches(4.3), Inches(12.1), Inches(2.1),
     "Built-in guardrails (the compliance layer)",
     ["Grounding + citations: every answer traces to the plan's official documents.   "
      "•  Scope limiter: navigation & education, never medical or insurance advice.",
      "No-steering enforcement: neutral plan comparisons (CMS marketing-rule safe).   "
      "•  PHI minimization + immutable audit logs.   •  Human-in-the-loop escalation."],
     TEAL, 16)

# ================================================================ SLIDE 7  Market
s = slide()
header(s, "MARKET SIZE", "Large, growing, and reachable through payers & brokers", 7)
# concentric circles
cx = Inches(3.4); cy = Inches(4.3)
for r_in, color, in [(2.4, RGBColor(0xD6,0xE6,0xF5)),
                     (1.7, RGBColor(0x9F,0xC4,0xE8)),
                     (1.0, BLUE)]:
    d = Inches(r_in*2)
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, cx-Inches(r_in), cy-Inches(r_in), d, d)
    c.fill.solid(); c.fill.fore_color.rgb = color
    c.line.fill.background(); c.shadow.inherit = False
def lbl(y, t, sz, col, bold=True):
    b,f = textbox(s, Inches(1.4), y, Inches(4.0), Inches(0.5), MSO_ANCHOR.MIDDLE)
    setpara(f.paragraphs[0], t, sz, col, bold=bold, align=PP_ALIGN.CENTER)
lbl(Inches(2.2), "TAM · ~68M Medicare beneficiaries", 13, NAVY)
lbl(Inches(3.6), "SAM · 33M+ MA members (growing)", 12, NAVY)
lbl(Inches(4.4), "SOM · regional plans + FMOs", 12, WHITE)
card(s, Inches(6.9), Inches(2.0), Inches(5.8), Inches(4.5),
     "How we capture it",
     ["TAM — all Medicare beneficiaries plus the payers, brokers, and FMOs that serve them.",
      "SAM — Medicare Advantage members and the plans / agencies that must educate and retain them.",
      "SOM (Yr 1–3) — beachhead of 3–5 regional MA plans and a broker / FMO network.",
      "",
      "Note: replace every figure with a current, sourced number (CMS / KFF) before pitching."],
     TEAL, 16)

# ================================================================ SLIDE 8  Business model
s = slide()
header(s, "BUSINESS MODEL", "Multi-sided, recurring revenue", 8)
cw = Inches(3.85); x0 = Inches(0.6); y0 = Inches(2.0); ch = Inches(3.5)
card(s, x0, y0, cw, ch, "B2B2C SaaS to payers",
     ["Per-member-per-month (PMPM) for the navigation + call-deflection layer.",
      "Sold to Medicare Advantage plans & payers."], BLUE)
card(s, x0+cw+gap, y0, cw, ch, "Broker / FMO seats",
     ["Per-seat or per-enrollment agent-assist during AEP / OEP.",
      "Speeds quoting and reduces errors."], TEAL)
card(s, x0+2*(cw+gap), y0, cw, ch, "Translation API",
     ["Usage-based plain-language conversion of plan documents.",
      "Drives 508 / accessibility compliance."], AMBER)
tb, tf = textbox(s, Inches(0.6), Inches(5.7), Inches(12), Inches(1.0))
setpara(tf.paragraphs[0],
        "Why plans buy: deflection + retention + Star-Rating (CAHPS) upside dwarfs the PMPM price.",
        15, NAVY, bold=True, italic=True)

# ================================================================ SLIDE 9  ROI
s = slide()
header(s, "ROI / UNIT ECONOMICS", "The buyer's payback math (illustrative — verify)", 9)
data = [
    ["Value lever", "Mechanism", "Illustrative benchmark"],
    ["Call deflection", "Contain repetitive 'is it covered / how do I' contacts",
     "$5–$12+ per live call → pennies–<$1 self-service"],
    ["Lower handle time", "AI surfaces grounded answers for agent-assist",
     "Shorter AHT on contained + escalated calls"],
    ["Retention", "Better plan fit reduces rapid disenrollment",
     "Hundreds of $ saved per retained member-year"],
    ["Accessibility ops", "Automated plain-language + translation",
     "Manual 508 remediation cost avoided"],
    ["Star Ratings", "Comprehension lifts CAHPS member experience",
     "Quality-bonus revenue upside (MA-specific)"],
]
table(s, 6, 3, Inches(0.6), Inches(2.0), Inches(12.1), Inches(3.0), data,
      col_widths=[Inches(2.6), Inches(4.6), Inches(4.9)], font_size=12)
card(s, Inches(0.6), Inches(5.2), Inches(12.1), Inches(1.5),
     "Payback formula (CFO-editable)",
     ["Annual savings = eligible contacts/member/yr × members × deflection rate × (cost/call − cost/AI). "
      "Add retention + accessibility + Star upside.",
      "Even at a conservative 20–30% containment on the navigational call segment, deflection alone "
      "pays back the PMPM in under [X] months — before retention and Star upside."],
     TEAL, 15)

# ================================================================ SLIDE 10 Compliance
s = slide()
header(s, "REGULATORY & COMPLIANCE", "We turn regulatory risk into a moat", 10)
phases = [
    ("Phase 0 · Foundation", "HIPAA program + BAAs, encryption, PHI minimization, audit logs, "
     "guardrails (no advice / no steering), CMS marketing-rule copy review", AMBER, "now"),
    ("Phase 1 · Enterprise-ready", "SOC 2 Type I, WCAG 2.x AA + VPAT, penetration test, "
     "incident-response runbook", BLUE, "before 1st paid contract"),
    ("Phase 2 · Scale", "SOC 2 Type II, AI governance + bias/accuracy monitoring, DPIAs, "
     "state-by-state activity review", TEAL, "Series A scale-up"),
    ("Phase 3 · Moat", "Continuous compliance automation, third-party audits, "
     "CMS-aligned transparency reporting", NAVY, "Series A → B"),
]
y = Inches(2.1); rh = Inches(1.05)
for title, body, color, when in phases:
    rect(s, Inches(0.6), y, Inches(0.18), rh - Inches(0.15), color)
    rect(s, Inches(0.9), y, Inches(11.8), rh - Inches(0.15), LIGHT)
    tb, tf = textbox(s, Inches(1.1), y + Inches(0.05), Inches(11.4), rh - Inches(0.2))
    p = tf.paragraphs[0]
    setpara(p, title, 15, NAVY, bold=True, space_after=2)
    r2 = p.add_run(); r2.text = "    (" + when + ")"
    r2.font.size = Pt(12); r2.font.italic = True; r2.font.color.rgb = SLATE; r2.font.name = FONT
    add_para(tf, body, 12, INK, space_after=0)
    y = y + rh

# ================================================================ SLIDE 11 Traction
s = slide()
header(s, "TRACTION & MARKET READINESS", "We can sell into MA enrollment today", 11)
cards = [
    ("Regulatory readiness", ["HIPAA in place; SOC 2 underway.",
      "CMS marketing-rule review complete.", "= legal to deploy in MA channels."], BLUE),
    ("Quality readiness", ["Accuracy benchmarked vs. human experts.",
      "Readability: grade 12.4 → 5.8 on real docs.", "Safety / guardrail evals passing."], TEAL),
    ("Commercial readiness", ["Signed pilots & design partners.",
      "LOIs from plans / FMOs.", "Named logos (where permitted)."], AMBER),
]
cw = Inches(3.85); x0 = Inches(0.6); y0 = Inches(2.0); ch = Inches(2.7)
for i,(t,lines,c) in enumerate(cards):
    card(s, x0 + i*(cw+gap), y0, cw, ch, t, lines, c)
# metrics band
rect(s, Inches(0.6), Inches(5.0), Inches(12.1), Inches(1.4), NAVY)
mets = [("Accuracy", "vs. human gold set"), ("Deflection", "of eligible contacts"),
        ("Languages", "supported"), ("Readability Δ", "grade-level drop")]
mw = Inches(12.1)/4
for i,(big,small) in enumerate(mets):
    bx = Inches(0.6) + mw*i
    tb,tf = textbox(s, bx, Inches(5.15), mw, Inches(1.1), MSO_ANCHOR.MIDDLE)
    setpara(tf.paragraphs[0], big, 18, AMBER, bold=True, align=PP_ALIGN.CENTER, space_after=2)
    add_para(tf, small, 12, WHITE, align=PP_ALIGN.CENTER, space_after=0)

# ================================================================ SLIDE 12 Competition
s = slide()
header(s, "COMPETITIVE LANDSCAPE", "Grounded + compliant = defensible", 12)
data = [
    ["", "Grounded\n& cited", "Real-time\nvoice", "Multilingual\n≤6th grade",
     "Compliance-\nfirst", "Plan data\nintegration"],
    ["ClariCare", "✓", "✓", "✓", "✓", "✓"],
    ["Plan-finder / comparison sites", "partial", "—", "partial", "partial", "partial"],
    ["Call-center BPOs", "—", "✓", "partial", "✓", "—"],
    ["Generic LLM chatbots", "—", "partial", "✓", "—", "—"],
    ["Broker software", "partial", "—", "—", "partial", "✓"],
]
table(s, 6, 6, Inches(0.6), Inches(2.1), Inches(12.1), Inches(3.4), data,
      col_widths=[Inches(3.6)] + [Inches(1.7)]*5, font_size=12, header_size=11)
tb, tf = textbox(s, Inches(0.6), Inches(5.8), Inches(12), Inches(0.9))
setpara(tf.paragraphs[0],
        "Defensibility = proprietary plan-document ingestion + compliance posture + multilingual voice + payer integrations.",
        14, NAVY, bold=True, italic=True)

# ================================================================ SLIDE 13 Team
s = slide()
header(s, "TEAM", "The trifecta a regulated market demands", 13)
roles = [
    ("Healthcare / payer domain", ["Knows MA operations, Star Ratings, and how plans buy."], BLUE),
    ("AI / ML engineering", ["Builds grounded, safe, multilingual conversational systems at scale."], TEAL),
    ("Regulatory / compliance", ["HIPAA, CMS marketing rules, SOC 2 — credibility with risk-averse payers."], AMBER),
]
cw = Inches(3.85); x0 = Inches(0.6); y0 = Inches(2.0); ch = Inches(2.8)
for i,(t,lines,c) in enumerate(roles):
    card(s, x0 + i*(cw+gap), y0, cw, ch, t, lines, c)
card(s, Inches(0.6), Inches(5.1), Inches(12.1), Inches(1.4),
     "Advisors", ["CMS / Medicare Advantage operating leaders, a health-equity expert, "
                  "and a healthcare regulatory counsel — replace with your real names & logos."], NAVY, 16)

# ================================================================ SLIDE 14 Ask
s = slide()
rect(s, 0, 0, SW, SH, NAVY)
rect(s, 0, Inches(2.4), SW, Inches(0.10), AMBER)
tb, tf = textbox(s, Inches(0.9), Inches(0.7), Inches(11.5), Inches(1.6))
setpara(tf.paragraphs[0], "The Ask", 44, WHITE, bold=True, space_after=4)
add_para(tf, "Raising $[X]M to make Medicare navigation conversational, "
             "readable, and compliant.", 20, AMBER, space_after=0)
# milestones
cols = [("Design partners", "→ paying plans"), ("SOC 2 Type II", "+ AI governance"),
        ("[N] members", "served"), ("$[X] ARR", "in 18 months")]
mw = Inches(2.85); x = Inches(0.9); y = Inches(3.0)
for big, small in cols:
    rect(s, x, y, mw, Inches(1.5), RGBColor(0x14,0x3A,0x5E))
    tbx, tfx = textbox(s, x, y+Inches(0.2), mw, Inches(1.1), MSO_ANCHOR.MIDDLE)
    setpara(tfx.paragraphs[0], big, 18, WHITE, bold=True, align=PP_ALIGN.CENTER, space_after=2)
    add_para(tfx, small, 13, RGBColor(0xC9,0xD8,0xE8), align=PP_ALIGN.CENTER, space_after=0)
    x = x + mw + Inches(0.13)
tb, tf = textbox(s, Inches(0.9), Inches(4.9), Inches(11.5), Inches(2.0))
setpara(tf.paragraphs[0], "Use of funds", 18, AMBER, bold=True, space_after=6)
add_para(tf, "Engineering & product  ·  Compliance & security  ·  Go-to-market (AEP/OEP)",
         16, WHITE, space_after=14)
add_para(tf, "Every dollar tied to a de-risking milestone the next round will underwrite.",
         15, RGBColor(0xC9,0xD8,0xE8), italic=True, space_after=0)
tb, tf = textbox(s, Inches(0.9), Inches(6.8), Inches(11.5), Inches(0.5))
setpara(tf.paragraphs[0], "Contact: finlawzicky7@gmail.com", 13, WHITE)

prs.save("medicare-advantage-investor-pitch.pptx")
print("Saved medicare-advantage-investor-pitch.pptx with", len(prs.slides._sldIdLst), "slides")
