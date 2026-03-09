"""Scheduler — polls Telegram for commands, runs periodic scans and updates."""

import time
import signal
import sys
from datetime import datetime

from assistant.telegram_bot import send_message, send_daily_summary, get_updates
from assistant.task_manager import (
    list_tasks, add_task, complete_task, get_due_reminders, mark_reminder_sent,
)
from assistant.system_monitor import generate_health_report
from assistant.opportunity_scraper import discover_opportunities, format_opportunities_report
from assistant.market_tracker import (
    fetch_crypto_prices, fetch_trending_coins, check_price_alerts,
    add_to_watchlist, remove_from_watchlist,
    format_price_report, format_alerts, format_trending,
)
from assistant.email_monitor import check_inbox, format_email_alerts
from assistant.github_tracker import (
    find_new_repos_by_language, find_bounty_issues,
    format_trending_report, format_bounty_report,
)
from assistant.opportunity_scorer import (
    rank_opportunities, get_top_opportunities, dismiss_opportunity,
    format_scored_report,
)


POLL_INTERVAL = 10  # Poll Telegram every 10 seconds
HEAVY_CHECK_INTERVAL = 30 * 60  # 30 minutes for price alerts, reminders
DAILY_SUMMARY_HOUR = 9
OPPORTUNITY_CHECK_HOURS = [8, 14, 20]


def handle_telegram_commands():
    """Process incoming Telegram messages as commands."""
    updates = get_updates(timeout=5)
    for update in updates:
        msg = update.get("message", {})
        text = msg.get("text", "").strip()

        if not text:
            continue

        try:
            _dispatch_command(text)
        except Exception as e:
            print(f"[Command] Error handling '{text}': {e}")
            send_message(f"Error: {e}")


def _dispatch_command(text):
    """Route a command to its handler."""
    # --- Task Management ---
    if text.startswith("/tasks"):
        tasks = list_tasks("active")
        if tasks:
            reply = "*Active Tasks:*\n"
            for t in tasks:
                reply += f"  • [{t['id']}] {t['title']}\n"
        else:
            reply = "No active tasks."
        send_message(reply)

    elif text.startswith("/add "):
        title = text[5:].strip()
        if title:
            task = add_task(title)
            send_message(f"Task added: *{task['title']}* (ID: {task['id']})")

    elif text.startswith("/done "):
        try:
            task_id = int(text[6:].strip())
            task = complete_task(task_id)
            if task:
                send_message(f"Completed: *{task['title']}*")
            else:
                send_message(f"Task {task_id} not found.")
        except ValueError:
            send_message("Usage: /done <task_id>")

    # --- System ---
    elif text.startswith("/health"):
        report = generate_health_report()
        send_message(report)

    # --- Market & Crypto ---
    elif text.startswith("/prices"):
        prices = fetch_crypto_prices()
        send_message(format_price_report(prices))

    elif text.startswith("/trending"):
        trending = fetch_trending_coins()
        send_message(format_trending(trending))

    elif text.startswith("/watchadd "):
        coin = text[10:].strip().lower()
        wl = add_to_watchlist(coin)
        send_message(f"Watchlist updated: {', '.join(wl)}")

    elif text.startswith("/watchdel "):
        coin = text[10:].strip().lower()
        wl = remove_from_watchlist(coin)
        send_message(f"Watchlist updated: {', '.join(wl)}")

    # --- Opportunities ---
    elif text.startswith("/opps") or text.startswith("/opportunities"):
        send_message("Scanning for opportunities...")
        opps = discover_opportunities()
        if opps:
            scored = rank_opportunities(opps)
            send_message(format_scored_report(scored))
        else:
            send_message("No new opportunities found since last scan.")

    elif text.startswith("/top"):
        top = get_top_opportunities(limit=10)
        send_message(format_scored_report(top))

    elif text.startswith("/dismiss "):
        try:
            idx = int(text[9:].strip()) - 1
            dismissed = dismiss_opportunity(idx)
            if dismissed:
                send_message(f"Dismissed: {dismissed.get('title', 'item')[:80]}")
            else:
                send_message("Invalid index.")
        except ValueError:
            send_message("Usage: /dismiss <number>")

    # --- GitHub ---
    elif text.startswith("/repos"):
        repos = find_new_repos_by_language()
        report = format_trending_report(repos)
        send_message(report or "No new trending repos found.")

    elif text.startswith("/bounties"):
        issues = find_bounty_issues()
        report = format_bounty_report(issues)
        send_message(report or "No bounty issues found.")

    # --- Email ---
    elif text.startswith("/emails"):
        flagged = check_inbox()
        report = format_email_alerts(flagged)
        send_message(report or "No opportunity emails found (or IMAP not configured).")

    # --- Help ---
    elif text.startswith("/help") or text.startswith("/start"):
        help_text = (
            "*📋 Task Management*\n"
            "/tasks — List active tasks\n"
            "/add <title> — Add a new task\n"
            "/done <id> — Complete a task\n\n"
            "*💰 Market & Crypto*\n"
            "/prices — Current crypto prices\n"
            "/trending — Trending coins\n"
            "/watchadd <coin> — Add to watchlist\n"
            "/watchdel <coin> — Remove from watchlist\n\n"
            "*🔍 Opportunities*\n"
            "/opps — Scan for new opportunities\n"
            "/top — Top scored opportunities\n"
            "/dismiss <n> — Dismiss opportunity #n\n\n"
            "*🐙 GitHub*\n"
            "/repos — Trending repos this week\n"
            "/bounties — Paid/bounty issues\n\n"
            "*📧 Email*\n"
            "/emails — Check inbox for opportunities\n\n"
            "*🖥️ System*\n"
            "/health — System health report\n"
            "/help — Show this help message"
        )
        send_message(help_text)


def check_reminders():
    """Send any due reminders."""
    due = get_due_reminders()
    for r in due:
        send_message(f"⏰ *Reminder:* {r['text']}")
        mark_reminder_sent(r["id"])


def run_opportunity_scan():
    """Autonomous opportunity scanning — runs at configured hours."""
    print(f"[{datetime.now()}] Running opportunity scan...")

    all_opportunities = []

    try:
        web_opps = discover_opportunities()
        all_opportunities.extend(web_opps)
    except Exception as e:
        print(f"[Opportunities] Web scrape error: {e}")

    try:
        repos = find_new_repos_by_language()
        all_opportunities.extend(repos)
        bounties = find_bounty_issues()
        all_opportunities.extend(bounties)
    except Exception as e:
        print(f"[Opportunities] GitHub error: {e}")

    try:
        emails = check_inbox()
        if emails:
            email_report = format_email_alerts(emails)
            if email_report:
                send_message(email_report)
    except Exception as e:
        print(f"[Opportunities] Email error: {e}")

    if all_opportunities:
        scored = rank_opportunities(all_opportunities)
        top = [s for s in scored if s.get("score", 0) >= 20]
        if top:
            send_message(format_scored_report(top, limit=5))

    print(f"[{datetime.now()}] Opportunity scan complete. Found {len(all_opportunities)} items.")


def run_heavy_checks():
    """Run expensive periodic checks (price alerts, opportunities, daily summary)."""
    now = datetime.now()
    print(f"[{now}] Running heavy checks...")

    # Check reminders
    check_reminders()

    # Check price alerts
    try:
        alerts = check_price_alerts()
        if alerts:
            alert_msg = format_alerts(alerts)
            if alert_msg:
                send_message(alert_msg)
    except Exception as e:
        print(f"[Market] Alert check error: {e}")

    # Run opportunity scan at configured hours
    if now.hour in OPPORTUNITY_CHECK_HOURS and now.minute < 30:
        try:
            run_opportunity_scan()
        except Exception as e:
            print(f"[Opportunities] Scan error: {e}")

    # Send daily summary at configured hour
    if now.hour == DAILY_SUMMARY_HOUR and now.minute < 30:
        active = [t["title"] for t in list_tasks("active")]
        completed = [t["title"] for t in list_tasks("completed")[-5:]]
        top_opps = get_top_opportunities(limit=3)
        notes = ""
        if top_opps:
            notes = "Top opportunities: " + ", ".join(
                o.get("title", "")[:50] for o in top_opps
            )
        send_daily_summary(active, completed, notes)

    print(f"[{now}] Heavy checks complete.")


def run():
    """Main scheduler loop — fast Telegram polling with periodic heavy checks."""
    print("Autonomous Assistant Scheduler started.")
    send_message("🤖 Assistant is online. Send /help for commands.")

    def signal_handler(sig, frame):
        print("\nShutting down scheduler...")
        send_message("🛑 Assistant scheduler stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    last_heavy_check = 0

    while True:
        try:
            # Fast: poll Telegram for commands every cycle
            handle_telegram_commands()
        except Exception as e:
            print(f"[Poll] Error: {e}")

        # Heavy checks every 30 minutes
        now = time.time()
        if now - last_heavy_check >= HEAVY_CHECK_INTERVAL:
            try:
                run_heavy_checks()
            except Exception as e:
                print(f"[Heavy] Error: {e}")
            last_heavy_check = now

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
