"""Task manager — reads/writes tasks from USER.md and a local tasks.json."""

import os
import json
import tempfile
from datetime import datetime

TASKS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks.json")
USER_MD = os.path.join(os.path.dirname(os.path.dirname(__file__)), "USER.md")


def _load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print("[Tasks] Corrupted tasks.json, starting fresh")
    return {"active": [], "completed": [], "reminders": [], "next_id": 1}


def _save_tasks(data):
    """Atomic write — write to temp file then rename."""
    dir_name = os.path.dirname(TASKS_FILE)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, TASKS_FILE)
    except OSError as e:
        print(f"[Tasks] Save failed: {e}")


def _next_id(data):
    """Get next unique task ID using a persistent counter."""
    next_id = data.get("next_id", 1)
    # Also ensure it's higher than any existing ID
    all_ids = [t.get("id", 0) for t in data["active"] + data["completed"]]
    if all_ids:
        next_id = max(next_id, max(all_ids) + 1)
    data["next_id"] = next_id + 1
    return next_id


def add_task(title, category="general", due=None, priority="normal"):
    """Add a new task."""
    data = _load_tasks()
    task = {
        "id": _next_id(data),
        "title": title,
        "category": category,
        "priority": priority,
        "due": due,
        "created": datetime.now().isoformat(),
        "status": "pending",
    }
    data["active"].append(task)
    _save_tasks(data)
    _sync_to_user_md(data)
    return task


def complete_task(task_id):
    """Mark a task as completed."""
    data = _load_tasks()
    for i, task in enumerate(data["active"]):
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            data["completed"].append(task)
            data["active"].pop(i)
            _save_tasks(data)
            _sync_to_user_md(data)
            return task
    return None


def list_tasks(status="active"):
    """List tasks by status."""
    data = _load_tasks()
    return data.get(status, [])


def add_reminder(text, remind_at):
    """Add a time-based reminder."""
    data = _load_tasks()
    reminder = {
        "id": _next_id(data),
        "text": text,
        "remind_at": remind_at,
        "created": datetime.now().isoformat(),
        "sent": False,
    }
    data.setdefault("reminders", []).append(reminder)
    _save_tasks(data)
    return reminder


def get_due_reminders():
    """Get reminders that are due now."""
    data = _load_tasks()
    now = datetime.now().isoformat()
    due = []
    for r in data.get("reminders", []):
        if not r["sent"] and r["remind_at"] <= now:
            due.append(r)
    return due


def mark_reminder_sent(reminder_id):
    """Mark a reminder as sent."""
    data = _load_tasks()
    for r in data.get("reminders", []):
        if r["id"] == reminder_id:
            r["sent"] = True
    _save_tasks(data)


def _sync_to_user_md(data):
    """Sync task state into USER.md."""
    if not os.path.exists(USER_MD):
        return

    try:
        with open(USER_MD) as f:
            content = f.read()
    except OSError:
        return

    # Build replacement sections
    active_section = "## Active Tasks\n"
    if data["active"]:
        for t in data["active"]:
            due = f" (due: {t['due']})" if t.get("due") else ""
            active_section += f"- [ ] [{t['category']}] {t['title']}{due}\n"
    else:
        active_section += "<!-- No active tasks -->\n"

    completed_section = "## Completed Tasks\n"
    for t in data["completed"][-10:]:
        completed_section += f"- [x] {t['title']} (completed {t.get('completed_at', 'N/A')})\n"
    if not data["completed"]:
        completed_section += "<!-- No completed tasks yet -->\n"

    # Rebuild USER.md with updated sections
    import re
    content = re.sub(
        r"## Active Tasks\n.*?(?=\n## |\Z)", active_section, content, flags=re.DOTALL
    )
    content = re.sub(
        r"## Completed Tasks\n.*?(?=\n## |\Z)", completed_section, content, flags=re.DOTALL
    )

    # Atomic write
    try:
        dir_name = os.path.dirname(USER_MD)
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp_path, USER_MD)
    except OSError as e:
        print(f"[Tasks] USER.md sync failed: {e}")
