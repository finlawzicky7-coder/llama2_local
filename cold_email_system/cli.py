"""CLI entry point for the Anubis AI cold email system."""

import argparse
import sys

from dotenv import load_dotenv

from .config import AppConfig
from .campaign import Campaign
from .prospects import load_prospects
from .templates.email_templates import TEMPLATES


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Anubis AI — Cold Email Outreach System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m cold_email_system send --dry-run\n"
            "  python -m cold_email_system send --template value_first --industry Healthcare\n"
            "  python -m cold_email_system follow-up --dry-run\n"
            "  python -m cold_email_system status\n"
            "  python -m cold_email_system preview --template initial_intro\n"
            "  python -m cold_email_system list-prospects\n"
        ),
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── send ───────────────────────────────────────────────────────
    send_parser = subparsers.add_parser("send", help="Send initial outreach emails")
    send_parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    send_parser.add_argument("--template", default="initial_intro", choices=list(TEMPLATES.keys()), help="Template to use")
    send_parser.add_argument("--industry", help="Filter prospects by industry")
    send_parser.add_argument("--limit", type=int, help="Max number of emails to send")

    # ── follow-up ──────────────────────────────────────────────────
    fu_parser = subparsers.add_parser("follow-up", help="Send follow-up emails")
    fu_parser.add_argument("--dry-run", action="store_true", help="Preview without sending")

    # ── status ─────────────────────────────────────────────────────
    subparsers.add_parser("status", help="Show campaign status")

    # ── preview ────────────────────────────────────────────────────
    preview_parser = subparsers.add_parser("preview", help="Preview a template")
    preview_parser.add_argument("--template", default="initial_intro", choices=list(TEMPLATES.keys()))

    # ── list-prospects ─────────────────────────────────────────────
    subparsers.add_parser("list-prospects", help="List all prospects from CSV")

    args = parser.parse_args()
    config = AppConfig()

    if args.command == "send":
        campaign = Campaign(config, dry_run=args.dry_run)
        campaign.run_initial_outreach(
            template_key=args.template,
            industry=args.industry,
            limit=args.limit,
        )

    elif args.command == "follow-up":
        campaign = Campaign(config, dry_run=args.dry_run)
        campaign.run_follow_ups()

    elif args.command == "status":
        campaign = Campaign(config, dry_run=True)
        campaign.show_status()

    elif args.command == "preview":
        tpl = TEMPLATES[args.template]
        print(f"\n── Template: {args.template} ──")
        print(f"Subject: {tpl['subject']}")
        print(f"\n{tpl['body']}")

    elif args.command == "list-prospects":
        prospects = load_prospects(config.prospects_csv)
        print(f"\n{'Email':<30} {'Name':<15} {'Company':<25} {'Industry':<15}")
        print("─" * 85)
        for p in prospects:
            print(f"{p.email:<30} {p.first_name:<15} {p.company:<25} {p.industry:<15}")
        print(f"\nTotal: {len(prospects)} prospects")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
