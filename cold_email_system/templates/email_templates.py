"""Email templates for Anubis AI cold outreach campaigns.

Each template uses Python string .format() placeholders:
  {first_name}    - Prospect's first name
  {company}       - Prospect's company name
  {industry}      - Prospect's industry
  {pain_point}    - A specific pain point relevant to their business
  {sender_name}   - The sender's name
"""

TEMPLATES = {
    # ── Stage 1: Initial Outreach ──────────────────────────────────
    "initial_intro": {
        "subject": "{first_name}, quick question about {company}'s AI strategy",
        "body": (
            "Hi {first_name},\n\n"
            "I came across {company} and noticed you're in the {industry} space. "
            "Many companies in your industry are leaving significant revenue on the table "
            "by not leveraging AI to {pain_point}.\n\n"
            "At Anubis AI, we help businesses like {company} deploy custom AI solutions "
            "that integrate directly into existing workflows — no rip-and-replace required.\n\n"
            "Our clients typically see results within the first 30 days:\n"
            "  - 40-60% reduction in manual processing time\n"
            "  - 3x faster response times to customers\n"
            "  - Measurable ROI within the first quarter\n\n"
            "Would you be open to a 15-minute call this week to see if there's a fit?\n\n"
            "Best,\n"
            "{sender_name}\n"
            "Anubis AI"
        ),
    },
    "value_first": {
        "subject": "Idea for {company}: AI-powered {pain_point}",
        "body": (
            "Hi {first_name},\n\n"
            "I put together a quick analysis of how {company} could use AI to "
            "{pain_point} — happy to share it, no strings attached.\n\n"
            "We've helped other {industry} companies implement similar solutions "
            "and the results have been significant.\n\n"
            "Want me to send it over?\n\n"
            "Best,\n"
            "{sender_name}\n"
            "Anubis AI"
        ),
    },
    # ── Stage 2: Follow-Up ─────────────────────────────────────────
    "follow_up_1": {
        "subject": "Re: {first_name}, quick question about {company}'s AI strategy",
        "body": (
            "Hi {first_name},\n\n"
            "Just wanted to float this back to the top of your inbox. "
            "I know things get busy.\n\n"
            "We recently helped a company in the {industry} space automate their "
            "{pain_point} process, cutting costs by 45% in the first quarter.\n\n"
            "If that kind of result would move the needle for {company}, I'd love "
            "to share how we did it.\n\n"
            "Worth a quick chat?\n\n"
            "Best,\n"
            "{sender_name}\n"
            "Anubis AI"
        ),
    },
    "follow_up_2": {
        "subject": "Re: {first_name}, quick question about {company}'s AI strategy",
        "body": (
            "Hi {first_name},\n\n"
            "I'll keep this short — I've been thinking about how {company} could "
            "benefit from AI-driven {pain_point} and wanted to share one concrete idea:\n\n"
            "We could set up an automated pipeline that handles the repetitive parts "
            "of your {pain_point} workflow, freeing your team to focus on high-value work.\n\n"
            "No commitment needed — just 15 minutes to see if it makes sense.\n\n"
            "Best,\n"
            "{sender_name}\n"
            "Anubis AI"
        ),
    },
    # ── Stage 3: Breakup Email ─────────────────────────────────────
    "breakup": {
        "subject": "Should I close your file, {first_name}?",
        "body": (
            "Hi {first_name},\n\n"
            "I've reached out a couple of times and haven't heard back, "
            "so I'll assume the timing isn't right.\n\n"
            "I'll close out your file for now, but if AI solutions for "
            "{pain_point} become a priority for {company} down the road, "
            "feel free to reach out anytime.\n\n"
            "Wishing you and the team all the best.\n\n"
            "Cheers,\n"
            "{sender_name}\n"
            "Anubis AI"
        ),
    },
}

# Map campaign stage number → template key
STAGE_SEQUENCE = [
    "initial_intro",
    "follow_up_1",
    "follow_up_2",
    "breakup",
]


def render_template(template_key: str, **kwargs) -> dict:
    """Render a template with the given variables. Returns {subject, body}."""
    template = TEMPLATES[template_key]
    return {
        "subject": template["subject"].format(**kwargs),
        "body": template["body"].format(**kwargs),
    }
