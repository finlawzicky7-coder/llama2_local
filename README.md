# Anubis AI — Cold Email Outreach System

A multi-stage cold email system for reaching out to businesses about Anubis AI's services.

## Features

- **Multi-stage sequences**: Initial outreach → Follow-up 1 → Follow-up 2 → Breakup email
- **Multiple templates**: Choose between different outreach styles (intro, value-first)
- **CSV-based prospect management**: Easy to import/export prospect lists
- **Rate limiting**: Configurable emails-per-hour with automatic throttling
- **Campaign tracking**: JSON-based log tracks every email sent, with stage tracking
- **Dry-run mode**: Preview all emails without sending
- **Industry filtering**: Target specific industries from your prospect list

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your SMTP credentials
cp .env.example .env
# Edit .env with your SMTP details

# 3. Add prospects to the CSV
# Edit cold_email_system/data/prospects.csv

# 4. Preview emails (dry run)
python -m cold_email_system send --dry-run

# 5. Send for real
python -m cold_email_system send
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `send` | Send initial outreach emails |
| `follow-up` | Send follow-up emails to non-responders |
| `status` | Show campaign statistics |
| `preview --template <name>` | Preview a specific template |
| `list-prospects` | List all prospects from CSV |

### Options

```
send:
  --dry-run              Preview without actually sending
  --template <name>      Template to use (initial_intro, value_first)
  --industry <name>      Filter prospects by industry
  --limit <n>            Max emails to send in this run

follow-up:
  --dry-run              Preview without actually sending
```

## Prospect CSV Format

| Column | Required | Description |
|--------|----------|-------------|
| email | Yes | Prospect's email address |
| first_name | Yes | First name for personalization |
| company | Yes | Company name |
| industry | Yes | Industry (for filtering) |
| pain_point | Yes | Specific pain point to address |
| title | No | Job title |
| website | No | Company website |
| notes | No | Internal notes |

## Configuration

All settings can be configured via environment variables (`.env` file):

- `SMTP_HOST` / `SMTP_PORT` — Mail server settings
- `SMTP_USERNAME` / `SMTP_PASSWORD` — SMTP credentials
- `SENDER_NAME` / `SENDER_EMAIL` — From address details
- `EMAILS_PER_HOUR` — Rate limit (default: 30)
- `DELAY_BETWEEN_EMAILS` — Seconds between sends (default: 120)
- `FOLLOW_UP_DELAY_DAYS` — Days to wait before follow-up (default: 3)
