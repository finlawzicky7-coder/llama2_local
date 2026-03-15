# CREBrokerAI

**All-in-One Commercial Real Estate Broker AI Platform**

CREBrokerAI automates the entire tenant-prospecting and leasing workflow for commercial real estate brokers using CrewAI multi-agent orchestration.

## Features

| Module | Description |
|--------|-------------|
| **Tenant Prospecting** | AI agents scan for companies with expiring leases, hiring growth, and funding signals |
| **Lead Scoring** | Predictive 1-100 scoring with hot/warm/cold tiers |
| **Property Matching** | Algorithmic matching of prospects to available inventory |
| **Outreach Campaign** | Personalized emails (SendGrid) and call scripts (Twilio) with CAN-SPAM/TCPA compliance |
| **Dashboard** | Streamlit UI with charts, filters, and one-click campaign execution |
| **REST API** | FastAPI microservice for integrations |

## Quick Start

```bash
# Install
pip install -e .

# Run mock campaign (no API keys needed)
crebrokerai run

# Launch dashboard
crebrokerai dashboard

# Launch API server
crebrokerai api
```

## Project Structure

```
crebrokerai/
├── __init__.py
├── __main__.py
├── cli.py                          # Typer CLI
├── main.py
├── config/
│   ├── settings.py                 # Pydantic Settings (.env loader)
│   ├── database.py                 # SQLAlchemy engine
│   └── models.py                   # ORM models
├── crews/
│   ├── prospecting/                # Lease scanner + growth analyst + profiler
│   │   ├── agents.yaml
│   │   ├── tasks.yaml
│   │   └── crew.py
│   ├── scoring/                    # Market analyst + lead scorer
│   │   ├── agents.yaml
│   │   ├── tasks.yaml
│   │   └── crew.py
│   ├── matching/                   # Property matcher + marketing creator
│   │   ├── agents.yaml
│   │   ├── tasks.yaml
│   │   └── crew.py
│   ├── outreach/                   # Email copywriter + call qualifier + coordinator
│   │   ├── agents.yaml
│   │   ├── tasks.yaml
│   │   └── crew.py
│   └── campaign/                   # Manager agent + QA reviewer
│       ├── agents.yaml
│       ├── tasks.yaml
│       └── crew.py
├── tools/
│   ├── cre_data.py                 # Mock CRE database tools
│   ├── email_tool.py               # SendGrid email with CAN-SPAM
│   ├── voice_tool.py               # Twilio voice with TCPA
│   ├── scoring_tool.py             # Deterministic lead scoring
│   └── matching_tool.py            # Property matching algorithm
├── data/
│   ├── mock_prospects.json         # 10 realistic prospect records
│   ├── mock_properties.json        # 10 realistic property listings
│   └── seed.py                     # Database seeder
├── api/
│   └── server.py                   # FastAPI application
├── dashboard/
│   └── app.py                      # Streamlit dashboard
└── utils/
    ├── logging.py                  # Rich logging
    ├── compliance.py               # CAN-SPAM + TCPA helpers
    └── export.py                   # CSV export
```

## Configuration

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | For full mode | Claude API key |
| `SENDGRID_API_KEY` | For real emails | SendGrid API key |
| `TWILIO_ACCOUNT_SID` | For real calls | Twilio SID |
| `SERPER_API_KEY` | For web search | Serper.dev key |

**Mock mode** runs with zero external keys — all tools return realistic simulated data.

## CLI Commands

```bash
crebrokerai run                    # Mock campaign
crebrokerai run --full             # Full LLM campaign
crebrokerai run -n "Q1 Campaign" -m "Austin,Miami" -i "Technology,Biotech"
crebrokerai dashboard              # Streamlit UI
crebrokerai api                    # FastAPI server
crebrokerai seed                   # Seed database
crebrokerai export                 # Export CSV reports
```

## Compliance

- **CAN-SPAM**: All emails include unsubscribe mechanism, physical address, and commercial advertisement disclosure
- **TCPA**: All calls include agent identification, brokerage name, and immediate opt-out option
- **Human-in-the-loop**: No real email or call is sent without explicit human approval

## Tech Stack

- **CrewAI** — Multi-agent orchestration
- **Anthropic Claude** — Default LLM (swappable to OpenAI/Groq)
- **Streamlit** — Dashboard UI
- **FastAPI** — REST API
- **SQLAlchemy** — ORM (SQLite default, PostgreSQL supported)
- **SendGrid** — Email delivery
- **Twilio** — Voice calls
- **Plotly** — Charts and visualizations

## License

MIT
