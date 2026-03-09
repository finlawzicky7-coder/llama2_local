"""Telegram integration for the autonomous assistant."""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

OFFSET_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".telegram_offset")


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


def _load_offset():
    """Load the last processed update_id."""
    try:
        if os.path.exists(OFFSET_FILE):
            with open(OFFSET_FILE) as f:
                return int(f.read().strip())
    except (ValueError, OSError):
        pass
    return None


def _save_offset(offset):
    """Save the last processed update_id."""
    try:
        with open(OFFSET_FILE, "w") as f:
            f.write(str(offset))
    except OSError as e:
        print(f"[Telegram] Failed to save offset: {e}")


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


def get_updates(timeout=10):
    """Get new messages sent to the bot, tracking offset to avoid duplicates."""
    config = load_config()
    token = config.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = config.get("TELEGRAM_CHAT_ID", "")

    if not token:
        return []

    offset = _load_offset()
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset

    data = urllib.parse.urlencode(params).encode()
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=timeout + 10) as resp:
            result = json.loads(resp.read())
            updates = result.get("result", [])

        if updates:
            # Only process messages from the configured chat
            if chat_id:
                updates = [
                    u for u in updates
                    if str(u.get("message", {}).get("chat", {}).get("id", "")) == str(chat_id)
                ]
            # Save offset as highest update_id + 1
            max_id = max(u["update_id"] for u in result.get("result", []))
            _save_offset(max_id + 1)

        return updates
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
