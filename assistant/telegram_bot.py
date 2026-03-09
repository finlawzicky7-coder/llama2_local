"""Telegram integration for the autonomous assistant."""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime


def load_config():
    """Load config from .env file."""
    config = {}
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config


def send_message(text, parse_mode="Markdown"):
    """Send a message via Telegram bot."""
    config = load_config()
    token = config.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = config.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id or chat_id == "SET_YOUR_CHAT_ID_HERE":
        print(f"[Telegram] Config incomplete. Message: {text}")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"[Telegram] Send failed: {e}")
        return False


def get_updates(offset=None):
    """Get new messages sent to the bot."""
    config = load_config()
    token = config.get("TELEGRAM_BOT_TOKEN", "")

    if not token:
        return []

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 5}
    if offset:
        params["offset"] = offset

    data = urllib.parse.urlencode(params).encode()
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get("result", [])
    except Exception as e:
        print(f"[Telegram] Get updates failed: {e}")
        return []


def send_daily_summary(tasks_pending, tasks_completed, notes=""):
    """Send a formatted daily summary."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"*Daily Summary — {now}*\n\n"

    if tasks_completed:
        msg += "*Completed:*\n"
        for t in tasks_completed:
            msg += f"  ✅ {t}\n"

    if tasks_pending:
        msg += "\n*Pending:*\n"
        for t in tasks_pending:
            msg += f"  ⏳ {t}\n"

    if notes:
        msg += f"\n*Notes:* {notes}"

    return send_message(msg)


if __name__ == "__main__":
    # Quick test
    send_message("🤖 Assistant is online and ready!")
