"""GitHub trending repos, bounties, and issue tracker for finding opportunities."""

import json
import urllib.request
import os
import re
import logging
from datetime import datetime, timedelta

log = logging.getLogger("github")

GITHUB_STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "github_state.json")


def _load_state():
    if os.path.exists(GITHUB_STATE_FILE):
        try:
            with open(GITHUB_STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "languages": ["python", "javascript", "rust", "go"],
        "seen_repos": [],
        "seen_issues": [],
        "last_check": None,
    }


def _save_state(data):
    data["last_check"] = datetime.now().isoformat()
    with open(GITHUB_STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _get_github_token():
    """Read GitHub token from .env if available."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    token = line.strip().split("=", 1)[1]
                    if token and token != "your_github_token":
                        return token
    return None


def _fetch_json(url, timeout=15):
    """Fetch a URL and parse JSON response."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; GHTracker/1.0)",
            "Accept": "application/vnd.github.v3+json",
        })
        token = _get_github_token()
        if token:
            req.add_header("Authorization", f"token {token}")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        log.warning("Fetch error (%s): %s", url, e)
        return None


def find_trending_repos(language=None, since="weekly"):
    """Find trending repos using GitHub search API (sorted by stars, created recently)."""
    state = _load_state()
    seen = set(state["seen_repos"])

    date_since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    query = f"created:>{date_since} stars:>50"
    if language:
        query += f" language:{language}"

    encoded_query = urllib.parse.quote(query) if hasattr(urllib, 'parse') else query
    url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page=15"
    data = _fetch_json(url)
    if not data:
        return []

    repos = []
    for repo in data.get("items", []):
        full_name = repo["full_name"]
        if full_name in seen:
            continue
        repos.append({
            "source": "GitHub",
            "name": full_name,
            "title": f"{full_name}: {(repo.get('description') or '')[:120]}",
            "description": (repo.get("description") or "")[:120],
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language", "Unknown"),
            "url": repo["html_url"],
            "topics": repo.get("topics", [])[:5],
        })
        seen.add(full_name)

    state["seen_repos"] = list(seen)[-500:]
    _save_state(state)
    return repos


# Need urllib.parse for query encoding
import urllib.parse


def _extract_bounty_amount(text, labels=None):
    """Extract bounty/reward dollar amount from issue text and labels."""
    # Check labels for amounts like "$500" or "bounty: $100"
    if labels:
        for label in labels:
            name = label.get("name", "") if isinstance(label, dict) else str(label)
            match = re.search(r"\$\s?([\d,]+(?:\.\d+)?)", name)
            if match:
                amount = float(match.group(1).replace(",", ""))
                if amount >= 10:
                    return {"amount": amount, "rate_type": "bounty", "raw": f"${amount:.0f} bounty"}

    # Check text body
    if text:
        # Look for bounty/reward amount patterns
        patterns = [
            re.compile(r"(?:bounty|reward|prize|payout)[:\s]*\$\s?([\d,]+)", re.I),
            re.compile(r"\$\s?([\d,]+)\s*(?:bounty|reward|prize|bonus)", re.I),
            re.compile(r"(?:pay|offer|budget)[:\s]*\$\s?([\d,]+)", re.I),
        ]
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                amount = float(match.group(1).replace(",", ""))
                if amount >= 10:
                    return {"amount": amount, "rate_type": "bounty", "raw": f"${amount:.0f} bounty"}

        # Generic dollar amount as fallback
        match = re.search(r"\$\s?([\d,]+)", text)
        if match:
            amount = float(match.group(1).replace(",", ""))
            if amount >= 50:  # Higher threshold for generic matches
                return {"amount": amount, "rate_type": "fixed", "raw": f"${amount:.0f}"}

    return None


def find_bounty_issues():
    """Find GitHub issues with bounty labels (paid work opportunities)."""
    state = _load_state()
    seen = set(state["seen_issues"])

    queries = [
        'label:bounty state:open',
        'label:paid state:open',
        'label:"help wanted" label:"good first issue" state:open',
        '"bounty" "$" state:open',
    ]

    issues = []
    for query in queries:
        encoded = urllib.parse.quote(query)
        url = f"https://api.github.com/search/issues?q={encoded}&sort=created&order=desc&per_page=15"
        data = _fetch_json(url)
        if not data:
            continue

        for item in data.get("items", []):
            issue_url = item["html_url"]
            if issue_url in seen:
                continue

            parts = issue_url.split("/")
            repo_name = "/".join(parts[3:5]) if len(parts) >= 5 else ""

            # Extract bounty amount from title, body, and labels
            searchable = (item.get("title", "") + " " + (item.get("body") or ""))
            pay = _extract_bounty_amount(searchable, item.get("labels", []))

            issue = {
                "source": "GitHub",
                "title": item["title"][:120],
                "repo": repo_name,
                "url": issue_url,
                "labels": [label["name"] for label in item.get("labels", [])[:5]],
                "created": item.get("created_at", ""),
            }
            if pay:
                issue["pay"] = pay
            issues.append(issue)
            seen.add(issue_url)

    state["seen_issues"] = list(seen)[-500:]
    _save_state(state)
    return issues


def find_new_repos_by_language():
    """Find new interesting repos across tracked languages."""
    state = _load_state()
    languages = state.get("languages", ["python", "javascript"])

    all_repos = []
    for lang in languages[:3]:
        repos = find_trending_repos(language=lang)
        all_repos.extend(repos)

    all_repos.sort(key=lambda r: r.get("stars", 0), reverse=True)
    return all_repos[:15]


def format_trending_report(repos, limit=10):
    """Format trending repos into a Telegram message."""
    if not repos:
        return None

    msg = f"*🔥 {len(repos)} Trending Repos*\n\n"
    for repo in repos[:limit]:
        topics = " ".join(f"`{t}`" for t in repo.get("topics", [])[:3])
        name = repo.get("name", repo.get("title", "Unknown"))
        msg += (
            f"⭐ *{repo['stars']}* — {name}\n"
            f"  {repo.get('description', '')}\n"
            f"  {repo.get('language', '')} {topics}\n"
            f"  {repo['url']}\n\n"
        )
    return msg


def format_bounty_report(issues, limit=10):
    """Format bounty issues into a Telegram message."""
    if not issues:
        return None

    # Sort by bounty amount (highest first)
    issues_sorted = sorted(issues, key=lambda x: x.get("pay", {}).get("amount", 0), reverse=True)

    msg = f"*💎 {len(issues)} Bounty/Paid Issues*\n\n"
    for issue in issues_sorted[:limit]:
        labels = ", ".join(issue.get("labels", [])[:3])
        repo = issue.get("repo", "")
        pay_str = ""
        if issue.get("pay"):
            pay_str = f" 💵 {issue['pay']['raw']}"
        msg += (
            f"*{issue['title']}*{pay_str}\n"
            f"  `{repo}` | {labels}\n"
            f"  {issue['url']}\n\n"
        )
    return msg
