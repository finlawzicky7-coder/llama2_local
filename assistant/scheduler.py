"""Scheduler — runs periodic checks and sends updates via Telegram."""

import time
import signal
import sys
from datetime import datetime

from assistant.telegram_bot import send_message, send_daily_summary, get_updates
from assistant.task_manager import (
    list_tasks, add_task, complete_task, get_due_reminders, mark_reminder_sent,
)
from assistant.system_monitor import generate_health_report


CHECK_INTERVAL = 30 * 60  # 30 minutes in seconds
DAILY_SUMMARY_HOUR = 9  # Send daily summary at 9 AM


def handle_telegram_commands():
    """Process incoming Telegram messages as commands."""
    updates = get_updates()
    for update in updates:
        msg = update.get("message", {})
        text = msg.get("text", "").strip()

        if not text:
            continue

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

        elif text.startswith("/health"):
            report = generate_health_report()
            send_message(report)

        elif text.startswith("/help"):
            help_text = (
                "*Available Commands:*\n"
                "/tasks — List active tasks\n"
                "/add <title> — Add a new task\n"
                "/done <id> — Complete a task\n"
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


def run_periodic_check():
    """Run all periodic checks."""
    now = datetime.now()
    print(f"[{now}] Running periodic check...")

    # Check for Telegram commands
    handle_telegram_commands()

    # Check reminders
    check_reminders()

    # Send daily summary at configured hour
    if now.hour == DAILY_SUMMARY_HOUR and now.minute < 30:
        active = [t["title"] for t in list_tasks("active")]
        completed = [t["title"] for t in list_tasks("completed")[-5:]]
        send_daily_summary(active, completed)

    print(f"[{now}] Periodic check complete.")


def run():
    """Main scheduler loop."""
    print("Autonomous Assistant Scheduler started.")
    send_message("🤖 Assistant scheduler is now running.")

    def signal_handler(sig, frame):
        print("\nShutting down scheduler...")
        send_message("🛑 Assistant scheduler stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        try:
            run_periodic_check()
        except Exception as e:
            print(f"Error during periodic check: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
