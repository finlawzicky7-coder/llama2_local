"""Task manager — reads/writes tasks from USER.md and a local tasks.json."""

import os
import json
from datetime import datetime

TASKS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks.json")
USER_MD = os.path.join(os.path.dirname(os.path.dirname(__file__)), "USER.md")


def _load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE) as f:
            return json.load(f)
    return {"active": [], "completed": [], "reminders": []}


def _save_tasks(data):
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_task(title, category="general", due=None, priority="normal"):
    """Add a new task."""
    data = _load_tasks()
    task = {
        "id": len(data["active"]) + len(data["completed"]) + 1,
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
        "id": len(data.get("reminders", [])) + 1,
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

    with open(USER_MD) as f:
        content = f.read()

    # Replace active tasks section
    active_section = "## Active Tasks\n"
    if data["active"]:
        for t in data["active"]:
            due = f" (due: {t['due']})" if t.get("due") else ""
            active_section += f"- [ ] [{t['category']}] {t['title']}{due}\n"
    else:
        active_section += "<!-- No active tasks -->\n"

    # Replace completed tasks section
    completed_section = "## Completed Tasks\n"
    for t in data["completed"][-10:]:  # Keep last 10
        completed_section += f"- [x] {t['title']} (completed {t.get('completed_at', 'N/A')})\n"
    if not data["completed"]:
        completed_section += "<!-- No completed tasks yet -->\n"

    # Rebuild USER.md with updated sections
    import re
    content = re.sub(
        r"## Active Tasks\n.*?(?=\n## )", active_section + "\n", content, flags=re.DOTALL
    )
    content = re.sub(
        r"## Completed Tasks\n.*?(?=\n## )", completed_section + "\n", content, flags=re.DOTALL
    )

    with open(USER_MD, "w") as f:
        f.write(content)
