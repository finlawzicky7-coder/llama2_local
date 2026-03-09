"""Web scraper for discovering freelance gigs, grants, and paid opportunities."""

import json
import urllib.request
import urllib.parse
import re
import os
import logging
from datetime import datetime

log = logging.getLogger("scraper")

OPPORTUNITIES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "opportunities.json")

# Regex to extract dollar amounts from text
MONEY_PATTERNS = [
    re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*[kK]\b"),         # $50k, $120K
    re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*/\s*(?:hr|hour)", re.I),  # $75/hr
    re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*/\s*(?:yr|year|annual)", re.I),  # $120k/yr
    re.compile(r"\$\s?([\d,]+(?:\.\d+)?)"),                   # $500, $5,000
    re.compile(r"([\d,]+)\s*(?:USD|usd)"),                     # 5000 USD
]

RATE_PATTERN = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*/\s*(hr|hour|day|week|month|yr|year)", re.I)


def _load_opportunities():
    if os.path.exists(OPPORTUNITIES_FILE):
        try:
            with open(OPPORTUNITIES_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
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
        log.warning("Failed to fetch %s: %s", url, e)
        return None


def _fetch_json(url, timeout=15):
    """Fetch a URL and parse as JSON."""
    content = _fetch_url(url, timeout)
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
    return None


def extract_pay_info(text):
    """Extract pay/budget information from text. Returns dict with amount, rate_type, raw."""
    if not text:
        return None

    # Try rate pattern first ($X/hr, $X/day, etc.)
    rate_match = RATE_PATTERN.search(text)
    if rate_match:
        amount_str = rate_match.group(1).replace(",", "")
        rate_type = rate_match.group(2).lower()
        try:
            amount = float(amount_str)
            # Normalize to hourly for comparison
            hourly = amount
            if rate_type in ("day",):
                hourly = amount / 8
            elif rate_type in ("week",):
                hourly = amount / 40
            elif rate_type in ("month",):
                hourly = amount / 160
            elif rate_type in ("yr", "year"):
                hourly = amount / 2080
            return {
                "amount": amount,
                "rate_type": rate_type,
                "hourly_equiv": round(hourly, 2),
                "raw": rate_match.group(0),
            }
        except ValueError:
            pass

    # Try fixed amounts
    for pattern in MONEY_PATTERNS:
        match = pattern.search(text)
        if match:
            amount_str = match.group(1).replace(",", "")
            try:
                amount = float(amount_str)
                # Handle $50k notation
                if "k" in match.group(0).lower() or "K" in match.group(0):
                    amount *= 1000
                # Skip tiny amounts (likely not pay)
                if amount < 10:
                    continue
                return {
                    "amount": amount,
                    "rate_type": "fixed",
                    "hourly_equiv": None,
                    "raw": match.group(0),
                }
            except ValueError:
                continue

    return None


def scrape_hacker_news_hiring():
    """Scrape Hacker News 'Who is Hiring?' threads for freelance/remote gigs."""
    opportunities = []
    try:
        url = "https://hn.algolia.com/api/v1/search?query=who+is+hiring&tags=story&hitsPerPage=5"
        data = _fetch_json(url)
        if not data:
            return opportunities

        for hit in data.get("hits", []):
            title = hit.get("title", "")
            if "hiring" not in title.lower():
                continue

            story_id = hit.get("objectID")
            story = _fetch_json(f"https://hn.algolia.com/api/v1/items/{story_id}")
            if not story:
                continue

            for child in story.get("children", [])[:80]:  # Scan more comments
                text = child.get("text", "")
                if not text:
                    continue

                text_lower = text.lower()
                keywords_found = [kw for kw in ["remote", "freelance", "contract",
                                                 "part-time", "consulting", "contractor"]
                                  if kw in text_lower]
                if not keywords_found:
                    continue

                # Extract company name (first line, strip HTML)
                first_line = re.sub(r"<[^>]+>", "", text.split("\n")[0])[:150]
                pay = extract_pay_info(text)

                opp = {
                    "source": "HackerNews",
                    "title": first_line.strip(),
                    "url": f"https://news.ycombinator.com/item?id={child.get('id', '')}",
                    "keywords": keywords_found,
                    "found": datetime.now().isoformat(),
                }
                if pay:
                    opp["pay"] = pay
                opportunities.append(opp)

    except Exception as e:
        log.error("HN hiring error: %s", e)
    return opportunities


def scrape_remoteok():
    """Scrape RemoteOK job board JSON API for remote gigs."""
    opportunities = []
    try:
        url = "https://remoteok.com/api"
        data = _fetch_json(url)
        if not data or not isinstance(data, list):
            return opportunities

        # First item is metadata, skip it
        for job in data[1:30]:
            title = job.get("position", "")
            company = job.get("company", "")
            tags = job.get("tags", [])
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")
            job_url = job.get("url", "")

            pay = None
            if salary_min and salary_max:
                avg = (int(salary_min) + int(salary_max)) / 2
                pay = {
                    "amount": avg,
                    "rate_type": "year",
                    "hourly_equiv": round(avg / 2080, 2),
                    "raw": f"${salary_min}-${salary_max}/yr",
                }
            elif salary_min:
                pay = {
                    "amount": int(salary_min),
                    "rate_type": "year",
                    "hourly_equiv": round(int(salary_min) / 2080, 2),
                    "raw": f"${salary_min}+/yr",
                }

            opp = {
                "source": "RemoteOK",
                "title": f"{company}: {title}"[:150],
                "url": f"https://remoteok.com{job_url}" if job_url.startswith("/") else job_url,
                "keywords": tags[:5] if isinstance(tags, list) else [],
                "found": datetime.now().isoformat(),
            }
            if pay:
                opp["pay"] = pay
            opportunities.append(opp)

    except Exception as e:
        log.error("RemoteOK error: %s", e)
    return opportunities


def scrape_weworkremotely():
    """Scrape We Work Remotely RSS feed for remote jobs."""
    opportunities = []
    feeds = [
        "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    ]
    for feed_url in feeds:
        try:
            content = _fetch_url(feed_url)
            if not content:
                continue
            # Parse RSS items
            items = re.findall(r"<item>(.*?)</item>", content, re.DOTALL)
            for item_xml in items[:15]:
                title_match = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", item_xml)
                link_match = re.search(r"<link>(.*?)</link>", item_xml)
                desc_match = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", item_xml, re.DOTALL)

                title = title_match.group(1).strip() if title_match else ""
                link = link_match.group(1).strip() if link_match else ""
                desc = desc_match.group(1).strip() if desc_match else ""

                if not title or not link:
                    continue

                pay = extract_pay_info(title + " " + desc)
                opp = {
                    "source": "WeWorkRemotely",
                    "title": re.sub(r"<[^>]+>", "", title)[:150],
                    "url": link,
                    "keywords": ["remote"],
                    "found": datetime.now().isoformat(),
                }
                if pay:
                    opp["pay"] = pay
                opportunities.append(opp)

        except Exception as e:
            log.error("WWR feed error: %s", e)
    return opportunities


def scrape_github_topics():
    """Find trending topics and projects that might need contributors."""
    opportunities = []
    try:
        url = "https://api.github.com/search/repositories?q=help+wanted+good+first+issue&sort=updated&per_page=10"
        data = _fetch_json(url)
        if not data:
            return opportunities

        for repo in data.get("items", []):
            opportunities.append({
                "source": "GitHub",
                "title": f"{repo['full_name']}: {(repo.get('description') or 'No description')[:100]}",
                "url": repo["html_url"],
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language", "Unknown"),
                "found": datetime.now().isoformat(),
            })
    except Exception as e:
        log.error("GitHub topics error: %s", e)
    return opportunities


def scrape_rss_feeds():
    """Scrape RSS feeds for grant/opportunity announcements."""
    opportunities = []
    feeds = [
        "https://www.indiehackers.com/feed.xml",
    ]
    for feed_url in feeds:
        try:
            content = _fetch_url(feed_url)
            if not content:
                continue
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
            log.error("RSS feed error (%s): %s", feed_url, e)
    return opportunities


def discover_opportunities():
    """Run all scrapers and return new opportunities not yet seen."""
    data = _load_opportunities()
    seen_urls = set(data["seen"])

    all_opps = []
    all_opps.extend(scrape_hacker_news_hiring())
    all_opps.extend(scrape_remoteok())
    all_opps.extend(scrape_weworkremotely())
    all_opps.extend(scrape_github_topics())
    all_opps.extend(scrape_rss_feeds())

    new_opps = []
    for opp in all_opps:
        url = opp.get("url", "")
        if url and url not in seen_urls:
            new_opps.append(opp)
            seen_urls.add(url)

    data["seen"] = list(seen_urls)[-1000:]  # Cap seen list
    data["alerts"].extend(new_opps)
    data["alerts"] = data["alerts"][-500:]
    _save_opportunities(data)

    log.info("Scraped %d total, %d new opportunities", len(all_opps), len(new_opps))
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
        if opp.get("pay"):
            pay = opp["pay"]
            extras += f" 💵{pay['raw']}"
            if pay.get("hourly_equiv"):
                extras += f" (~${pay['hourly_equiv']:.0f}/hr)"
        if "stars" in opp:
            extras += f" ⭐{opp['stars']}"
        if "keywords" in opp:
            extras += f" [{', '.join(opp['keywords'][:3])}]"
        msg += f"*[{source}]* {title}{extras}\n{url}\n\n"

    if len(opps) > limit:
        msg += f"_...and {len(opps) - limit} more_"

    return msg
