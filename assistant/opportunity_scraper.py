"""Web scraper for discovering freelance gigs, grants, and opportunities."""

import json
import urllib.request
import urllib.parse
import re
import os
from datetime import datetime

OPPORTUNITIES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "opportunities.json")


def _load_opportunities():
    if os.path.exists(OPPORTUNITIES_FILE):
        with open(OPPORTUNITIES_FILE) as f:
            return json.load(f)
    return {"seen": [], "alerts": [], "last_check": None}


def _save_opportunities(data):
    data["last_check"] = datetime.now().isoformat()
    with open(OPPORTUNITIES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _fetch_url(url, timeout=15):
    """Fetch a URL and return its text content."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; OpportunityBot/1.0)"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[Scraper] Failed to fetch {url}: {e}")
        return None


def scrape_hacker_news_hiring():
    """Scrape Hacker News 'Who is Hiring?' threads for freelance/remote gigs."""
    opportunities = []
    try:
        # Search HN Algolia API for hiring posts
        url = "https://hn.algolia.com/api/v1/search?query=who+is+hiring&tags=story&hitsPerPage=5"
        content = _fetch_url(url)
        if not content:
            return opportunities

        data = json.loads(content)
        for hit in data.get("hits", []):
            title = hit.get("title", "")
            if "hiring" in title.lower():
                # Fetch comments (job listings) from the thread
                story_id = hit.get("objectID")
                comments_url = f"https://hn.algolia.com/api/v1/items/{story_id}"
                comments_data = _fetch_url(comments_url)
                if comments_data:
                    story = json.loads(comments_data)
                    for child in story.get("children", [])[:20]:
                        text = child.get("text", "")
                        if not text:
                            continue
                        # Look for remote, freelance, contract keywords
                        text_lower = text.lower()
                        if any(kw in text_lower for kw in ["remote", "freelance", "contract", "part-time", "consulting"]):
                            # Extract company name (usually first line)
                            first_line = re.sub(r"<[^>]+>", "", text.split("\n")[0])[:150]
                            opportunities.append({
                                "source": "HackerNews",
                                "title": first_line.strip(),
                                "url": f"https://news.ycombinator.com/item?id={child.get('id', '')}",
                                "keywords": [kw for kw in ["remote", "freelance", "contract", "consulting"]
                                           if kw in text_lower],
                                "found": datetime.now().isoformat(),
                            })
    except Exception as e:
        print(f"[Scraper] HN hiring error: {e}")
    return opportunities


def scrape_github_topics():
    """Find trending topics and projects that might need contributors."""
    opportunities = []
    try:
        url = "https://api.github.com/search/repositories?q=help+wanted+good+first+issue&sort=updated&per_page=10"
        content = _fetch_url(url)
        if not content:
            return opportunities

        data = json.loads(content)
        for repo in data.get("items", []):
            opportunities.append({
                "source": "GitHub",
                "title": f"{repo['full_name']}: {repo.get('description', 'No description')[:100]}",
                "url": repo["html_url"],
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language", "Unknown"),
                "found": datetime.now().isoformat(),
            })
    except Exception as e:
        print(f"[Scraper] GitHub topics error: {e}")
    return opportunities


def scrape_rss_feeds():
    """Scrape RSS feeds for grant/opportunity announcements."""
    opportunities = []
    feeds = [
        # IndieHackers, ProductHunt, etc. (RSS/JSON feeds)
        "https://www.indiehackers.com/feed.xml",
    ]
    for feed_url in feeds:
        try:
            content = _fetch_url(feed_url)
            if not content:
                continue
            # Simple XML title extraction
            titles = re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", content)
            links = re.findall(r"<link>(.*?)</link>", content)
            for i, title in enumerate(titles[:10]):
                title_lower = title.lower()
                if any(kw in title_lower for kw in ["launch", "revenue", "profit", "saas",
                                                      "startup", "freelance", "side project",
                                                      "passive income", "opportunity"]):
                    opportunities.append({
                        "source": "RSS",
                        "title": title.strip()[:150],
                        "url": links[i] if i < len(links) else feed_url,
                        "found": datetime.now().isoformat(),
                    })
        except Exception as e:
            print(f"[Scraper] RSS feed error ({feed_url}): {e}")
    return opportunities


def discover_opportunities():
    """Run all scrapers and return new opportunities not yet seen."""
    data = _load_opportunities()
    seen_urls = set(data["seen"])

    all_opps = []
    all_opps.extend(scrape_hacker_news_hiring())
    all_opps.extend(scrape_github_topics())
    all_opps.extend(scrape_rss_feeds())

    new_opps = []
    for opp in all_opps:
        if opp["url"] not in seen_urls:
            new_opps.append(opp)
            seen_urls.add(opp["url"])

    # Save state
    data["seen"] = list(seen_urls)
    data["alerts"].extend(new_opps)
    # Keep only last 200 alerts
    data["alerts"] = data["alerts"][-200:]
    _save_opportunities(data)

    return new_opps


def format_opportunities_report(opps, limit=10):
    """Format opportunities into a Telegram message."""
    if not opps:
        return None

    msg = f"*🔍 {len(opps)} New Opportunities Found*\n\n"
    for opp in opps[:limit]:
        source = opp.get("source", "Unknown")
        title = opp["title"][:100]
        url = opp["url"]
        extras = ""
        if "stars" in opp:
            extras = f" ⭐{opp['stars']}"
        if "keywords" in opp:
            extras += f" [{', '.join(opp['keywords'])}]"
        msg += f"*[{source}]* {title}{extras}\n{url}\n\n"

    if len(opps) > limit:
        msg += f"_...and {len(opps) - limit} more_"

    return msg
