"""System monitoring utilities for the assistant."""

import os
import subprocess
import shutil
from datetime import datetime


def get_disk_usage():
    """Get disk usage for key paths."""
    usage = shutil.disk_usage("/")
    return {
        "total_gb": round(usage.total / (1024**3), 1),
        "used_gb": round(usage.used / (1024**3), 1),
        "free_gb": round(usage.free / (1024**3), 1),
        "percent_used": round(usage.used / usage.total * 100, 1),
    }


def get_system_load():
    """Get system load averages."""
    try:
        load = os.getloadavg()
        return {"1min": load[0], "5min": load[1], "15min": load[2]}
    except OSError:
        return None


def get_running_processes(limit=10):
    """Get top processes by CPU usage."""
    try:
        result = subprocess.run(
            ["ps", "aux", "--sort=-pcpu"],
            capture_output=True, text=True, timeout=5,
        )
        lines = result.stdout.strip().split("\n")
        return lines[:limit + 1]  # header + top N
    except Exception:
        return []


def check_git_repos(paths=None):
    """Check git status of specified repos."""
    if paths is None:
        paths = [os.path.dirname(os.path.dirname(__file__))]

    results = []
    for path in paths:
        if os.path.isdir(os.path.join(path, ".git")):
            try:
                status = subprocess.run(
                    ["git", "-C", path, "status", "--porcelain"],
                    capture_output=True, text=True, timeout=5,
                )
                branch = subprocess.run(
                    ["git", "-C", path, "branch", "--show-current"],
                    capture_output=True, text=True, timeout=5,
                )
                results.append({
                    "path": path,
                    "branch": branch.stdout.strip(),
                    "dirty": bool(status.stdout.strip()),
                    "changes": len(status.stdout.strip().split("\n")) if status.stdout.strip() else 0,
                })
            except Exception:
                pass
    return results


def generate_health_report():
    """Generate a system health report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    disk = get_disk_usage()
    load = get_system_load()

    report = f"*System Health — {now}*\n\n"
    report += f"*Disk:* {disk['used_gb']}GB / {disk['total_gb']}GB ({disk['percent_used']}%)\n"

    if load:
        report += f"*Load:* {load['1min']:.2f} / {load['5min']:.2f} / {load['15min']:.2f}\n"

    repos = check_git_repos()
    if repos:
        report += "\n*Git Repos:*\n"
        for r in repos:
            status = "dirty" if r["dirty"] else "clean"
            report += f"  `{r['path']}` — {r['branch']} ({status})\n"

    if disk["percent_used"] > 90:
        report += "\n⚠️ *Warning: Disk usage above 90%!*"

    return report
