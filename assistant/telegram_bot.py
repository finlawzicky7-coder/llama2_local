"""Telegram integration for the autonomous assistant."""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

OFFSET_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".telegram_offset")

# Telegram message limit is 4096 chars
MAX_MESSAGE_LENGTH = 4000


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


def escape_markdown(text):
    """Escape Telegram Markdown V1 special characters in user-provided text."""
    for ch in ("*", "_", "`", "[", "]"):
        text = text.replace(ch, f"\\{ch}")
    return text


def send_message(text, parse_mode="Markdown"):
    """Send a message via Telegram bot. Splits long messages automatically."""
    config = load_config()
    token = config.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = config.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id or chat_id == "SET_YOUR_CHAT_ID_HERE":
        print(f"[Telegram] Config incomplete. Message: {text}")
        return False

    # Split long messages
    chunks = []
    while len(text) > MAX_MESSAGE_LENGTH:
        # Try to split at a newline
        split_at = text.rfind("\n", 0, MAX_MESSAGE_LENGTH)
        if split_at == -1:
            split_at = MAX_MESSAGE_LENGTH
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    chunks.append(text)

    success = True
    for chunk in chunks:
        if not chunk.strip():
            continue
        if not _send_single_message(token, chat_id, chunk, parse_mode):
            success = False
    return success


def _send_single_message(token, chat_id, text, parse_mode):
    """Send a single message chunk via Telegram API."""
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
        # If Markdown fails, retry without parse_mode
        if parse_mode:
            return _send_single_message(token, chat_id, text, parse_mode="")
        print(f"[Telegram] Send failed: {e}")
        return False


def get_updates(timeout=5):
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
            raw_updates = result.get("result", [])

        if not raw_updates:
            return []

        # Save offset as highest update_id + 1 (before filtering)
        max_id = max(u["update_id"] for u in raw_updates)
        _save_offset(max_id + 1)

        # Only process messages from the configured chat
        if chat_id:
            raw_updates = [
                u for u in raw_updates
                if str(u.get("message", {}).get("chat", {}).get("id", "")) == str(chat_id)
            ]

        return raw_updates
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
            msg += f"  ✅ {escape_markdown(t)}\n"

    if tasks_pending:
        msg += "\n*Pending:*\n"
        for t in tasks_pending:
            msg += f"  ⏳ {escape_markdown(t)}\n"

    if notes:
        msg += f"\n*Notes:* {escape_markdown(notes)}"

    return send_message(msg)


if __name__ == "__main__":
    send_message("🤖 Assistant is online and ready!")
