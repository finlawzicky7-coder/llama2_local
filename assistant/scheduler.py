"""Scheduler — polls Telegram for commands, runs periodic scans and updates."""

import json
import os
import time
import signal
import sys
import logging
from datetime import datetime, timedelta

from assistant.telegram_bot import send_message, send_daily_summary, get_updates, escape_markdown
from assistant.task_manager import (
    list_tasks, add_task, complete_task, add_reminder,
    get_due_reminders, mark_reminder_sent,
)
from assistant.system_monitor import generate_health_report
from assistant.opportunity_scraper import discover_opportunities, format_opportunities_report
from assistant.market_tracker import (
    fetch_crypto_prices, fetch_trending_coins, check_price_alerts,
    add_to_watchlist, remove_from_watchlist,
    format_price_report, format_alerts, format_trending,
    calculate_signals,
)
from assistant.email_monitor import check_inbox, format_email_alerts
from assistant.github_tracker import (
    find_new_repos_by_language, find_bounty_issues,
    format_trending_report, format_bounty_report,
)
from assistant.opportunity_scorer import (
    rank_opportunities, get_top_opportunities, dismiss_opportunity,
    format_scored_report, log_earning, format_earnings_report,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("scheduler")

POLL_INTERVAL = 10
HEAVY_CHECK_INTERVAL = 30 * 60
DAILY_SUMMARY_HOUR = 9
OPPORTUNITY_CHECK_HOURS = [8, 14, 20]

# Persistent state file to survive restarts
STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".scheduler_state.json")


def _load_state():
    """Load scheduler state from disk."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _save_state(state):
    """Save scheduler state to disk."""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except OSError as e:
        log.error("Failed to save state: %s", e)


def _already_ran_today(key):
    """Check if a task already ran during the current hour (survives restarts)."""
    state = _load_state()
    last_run = state.get(key, "")
    now_key = datetime.now().strftime("%Y-%m-%d-%H")
    return last_run == now_key


def _mark_ran(key):
    """Mark a task as having run during this hour."""
    state = _load_state()
    state[key] = datetime.now().strftime("%Y-%m-%d-%H")
    _save_state(state)


def _parse_remind_time(time_str):
    """Parse relative time like '30m', '2h', '1d' or absolute 'HH:MM'."""
    time_str = time_str.strip().lower()

    # Relative: 30m, 2h, 1d
    if time_str.endswith("m"):
        try:
            minutes = int(time_str[:-1])
            return (datetime.now() + timedelta(minutes=minutes)).isoformat()
        except ValueError:
            pass
    elif time_str.endswith("h"):
        try:
            hours = int(time_str[:-1])
            return (datetime.now() + timedelta(hours=hours)).isoformat()
        except ValueError:
            pass
    elif time_str.endswith("d"):
        try:
            days = int(time_str[:-1])
            return (datetime.now() + timedelta(days=days)).isoformat()
        except ValueError:
            pass

    # Absolute: HH:MM (today or tomorrow)
    try:
        hour, minute = time_str.split(":")
        target = datetime.now().replace(hour=int(hour), minute=int(minute), second=0)
        if target <= datetime.now():
            target += timedelta(days=1)
        return target.isoformat()
    except (ValueError, TypeError):
        pass

    return None


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
            log.error("Error handling command '%s': %s", text, e)
            send_message("Something went wrong processing your command. Try again.")


def _dispatch_command(text):
    """Route a command to its handler."""
    # --- Task Management ---
    if text.startswith("/tasks"):
        tasks = list_tasks("active")
        if tasks:
            reply = "*Active Tasks:*\n"
            for t in tasks:
                pri = ""
                if t.get("priority") == "high":
                    pri = "🔴 "
                reply += f"  • \\[{t['id']}] {pri}{escape_markdown(t['title'])}\n"
        else:
            reply = "No active tasks."
        send_message(reply)

    elif text.startswith("/add "):
        title = text[5:].strip()
        if title:
            task = add_task(title)
            send_message(f"Task added: *{escape_markdown(task['title'])}* (ID: {task['id']})")

    elif text.startswith("/done "):
        try:
            task_id = int(text[6:].strip())
            task = complete_task(task_id)
            if task:
                send_message(f"Completed: *{escape_markdown(task['title'])}*")
            else:
                send_message(f"Task {task_id} not found.")
        except ValueError:
            send_message("Usage: /done <task\\_id>")

    # --- Reminders ---
    elif text.startswith("/remind "):
        # /remind 30m Take a break
        # /remind 2h Check on deployment
        # /remind 14:00 Team standup
        parts = text[8:].strip().split(None, 1)
        if len(parts) >= 2:
            remind_at = _parse_remind_time(parts[0])
            if remind_at:
                reminder = add_reminder(parts[1], remind_at)
                target = datetime.fromisoformat(remind_at)
                time_str = target.strftime("%H:%M on %b %d")
                send_message(f"⏰ Reminder set for *{time_str}*: {escape_markdown(parts[1])}")
            else:
                send_message("Couldn't parse time. Use: 30m, 2h, 1d, or HH:MM")
        else:
            send_message("Usage: /remind <time> <text>\nExamples: /remind 30m Check email\n/remind 2h Follow up on gig\n/remind 14:00 Meeting")

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
        if coin:
            wl = add_to_watchlist(coin)
            send_message(f"Watchlist updated: {', '.join(wl)}")

    elif text.startswith("/watchdel "):
        coin = text[10:].strip().lower()
        if coin:
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
                title = escape_markdown(dismissed.get("title", "item")[:80])
                send_message(f"Dismissed: {title}")
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

    # --- Earnings Tracking ---
    elif text.startswith("/earned "):
        parts = text[8:].strip().split(None, 2)
        if len(parts) >= 2:
            try:
                amount = float(parts[0].replace("$", "").replace(",", ""))
                source = parts[1]
                desc = parts[2] if len(parts) > 2 else ""
                log_earning(amount, source, desc)
                send_message(f"Logged *${amount:,.2f}* from {escape_markdown(source)}")
            except ValueError:
                send_message("Usage: /earned <amount> <source> [description]")
        else:
            send_message("Usage: /earned 500 freelance fixed a React bug")

    elif text.startswith("/earnings"):
        send_message(format_earnings_report())

    # --- Trading Signals ---
    elif text.startswith("/signals"):
        signals = calculate_signals()
        if signals:
            msg = "*📊 Trading Signals*\n\n"
            for coin, sig in signals.items():
                msg += f"*{escape_markdown(coin.title())}* — ${sig['price']:,.2f}\n"
                if sig.get("rsi"):
                    msg += f"  RSI: {sig['rsi']}\n"
                msg += f"  Trend: {sig['trend']}\n"
                for s in sig["signals"]:
                    msg += f"  {s}\n"
                msg += "\n"
            send_message(msg)
        else:
            send_message("Not enough data for signals yet. Need ~5 price snapshots.")

    # --- Help ---
    elif text.startswith("/help") or text.startswith("/start"):
        help_text = (
            "*Task Management*\n"
            "/tasks — List active tasks\n"
            "/add <title> — Add a new task\n"
            "/done <id> — Complete a task\n"
            "/remind <time> <text> — Set a reminder\n\n"
            "*Market & Crypto*\n"
            "/prices — Prices + trading signals\n"
            "/signals — RSI, momentum, volume analysis\n"
            "/trending — Trending coins\n"
            "/watchadd <coin> — Add to watchlist\n"
            "/watchdel <coin> — Remove from watchlist\n\n"
            "*Opportunities*\n"
            "/opps — Scan for paid opportunities\n"
            "/top — Top scored opportunities\n"
            "/dismiss <n> — Dismiss opportunity #n\n\n"
            "*GitHub*\n"
            "/repos — Trending repos this week\n"
            "/bounties — Paid/bounty issues\n\n"
            "*Earnings*\n"
            "/earned <amt> <source> — Log income\n"
            "/earnings — View earnings summary\n\n"
            "*Email*\n"
            "/emails — Check inbox for opportunities\n\n"
            "*System*\n"
            "/health — System health report\n"
            "/help — Show this help message"
        )
        send_message(help_text)


def check_reminders():
    """Send any due reminders."""
    due = get_due_reminders()
    for r in due:
        send_message(f"⏰ *Reminder:* {escape_markdown(r['text'])}")
        mark_reminder_sent(r["id"])


def run_opportunity_scan():
    """Autonomous opportunity scanning — runs at configured hours."""
    log.info("Running opportunity scan...")

    all_opportunities = []

    try:
        web_opps = discover_opportunities()
        all_opportunities.extend(web_opps)
    except Exception as e:
        log.error("Web scrape error: %s", e)

    try:
        repos = find_new_repos_by_language()
        all_opportunities.extend(repos)
        bounties = find_bounty_issues()
        all_opportunities.extend(bounties)
    except Exception as e:
        log.error("GitHub error: %s", e)

    try:
        emails = check_inbox()
        if emails:
            email_report = format_email_alerts(emails)
            if email_report:
                send_message(email_report)
    except Exception as e:
        log.error("Email error: %s", e)

    if all_opportunities:
        scored = rank_opportunities(all_opportunities)
        top = [s for s in scored if s.get("score", 0) >= 20]
        if top:
            send_message(format_scored_report(top, limit=5))

    log.info("Opportunity scan complete. Found %d items.", len(all_opportunities))


def run_heavy_checks():
    """Run expensive periodic checks (price alerts, opportunities, daily summary)."""
    now = datetime.now()
    log.info("Running heavy checks...")

    check_reminders()

    try:
        alerts = check_price_alerts()
        if alerts:
            alert_msg = format_alerts(alerts)
            if alert_msg:
                send_message(alert_msg)
    except Exception as e:
        log.error("Price alert error: %s", e)

    # Run opportunity scan at configured hours (once per hour, persistent)
    if now.hour in OPPORTUNITY_CHECK_HOURS:
        opp_key = f"opp_scan_{now.hour}"
        if not _already_ran_today(opp_key):
            _mark_ran(opp_key)
            try:
                run_opportunity_scan()
            except Exception as e:
                log.error("Opportunity scan error: %s", e)

    # Send daily summary (once per day at configured hour, persistent)
    if now.hour == DAILY_SUMMARY_HOUR:
        summary_key = "daily_summary"
        if not _already_ran_today(summary_key):
            _mark_ran(summary_key)
            active = [t["title"] for t in list_tasks("active")]
            completed = [t["title"] for t in list_tasks("completed")[-5:]]
            top_opps = get_top_opportunities(limit=3)
            notes = ""
            if top_opps:
                notes = "Top opportunities: " + ", ".join(
                    o.get("title", "")[:50] for o in top_opps
                )
            send_daily_summary(active, completed, notes)

    log.info("Heavy checks complete.")


def run():
    """Main scheduler loop — fast Telegram polling with periodic heavy checks."""
    log.info("Autonomous Assistant Scheduler started.")
    send_message("🤖 Assistant is online. Send /help for commands.")

    def signal_handler(sig, frame):
        log.info("Shutting down scheduler...")
        send_message("🛑 Assistant scheduler stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    last_heavy_check = 0

    while True:
        try:
            handle_telegram_commands()
        except Exception as e:
            log.error("Telegram poll error: %s", e)

        now = time.time()
        if now - last_heavy_check >= HEAVY_CHECK_INTERVAL:
            try:
                run_heavy_checks()
            except Exception as e:
                log.error("Heavy check error: %s", e)
            last_heavy_check = now

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
