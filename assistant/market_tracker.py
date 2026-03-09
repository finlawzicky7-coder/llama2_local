"""Crypto and market price tracker using free public APIs."""

import json
import urllib.request
import os
from datetime import datetime

MARKET_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "market_data.json")

# Default watchlist — user can customize via Telegram /watchlist command
DEFAULT_WATCHLIST = ["bitcoin", "ethereum", "solana"]
DEFAULT_ALERT_THRESHOLDS = {
    "price_change_pct": 5.0,  # Alert if 24h change exceeds this %
}


def _load_market_data():
    if os.path.exists(MARKET_FILE):
        with open(MARKET_FILE) as f:
            return json.load(f)
    return {
        "watchlist": DEFAULT_WATCHLIST,
        "alert_thresholds": DEFAULT_ALERT_THRESHOLDS,
        "price_history": [],
        "alerts_sent": [],
    }


def _save_market_data(data):
    with open(MARKET_FILE, "w") as f:
        json.dump(data, f, indent=2)


def fetch_crypto_prices(coins=None):
    """Fetch current crypto prices from CoinGecko free API."""
    data = _load_market_data()
    if coins is None:
        coins = data.get("watchlist", DEFAULT_WATCHLIST)

    ids = ",".join(coins)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; MarketTracker/1.0)"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            prices = json.loads(resp.read())

        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "prices": prices,
        }
        data["price_history"].append(snapshot)
        # Keep last 100 snapshots
        data["price_history"] = data["price_history"][-100:]
        _save_market_data(data)
        return prices
    except Exception as e:
        print(f"[Market] Price fetch error: {e}")
        return None


def fetch_trending_coins():
    """Fetch trending coins from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; MarketTracker/1.0)"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return [
            {
                "name": coin["item"]["name"],
                "symbol": coin["item"]["symbol"],
                "rank": coin["item"]["market_cap_rank"],
            }
            for coin in data.get("coins", [])[:10]
        ]
    except Exception as e:
        print(f"[Market] Trending fetch error: {e}")
        return []


def check_price_alerts():
    """Check if any price movements exceed alert thresholds."""
    data = _load_market_data()
    threshold = data.get("alert_thresholds", DEFAULT_ALERT_THRESHOLDS)
    pct_limit = threshold.get("price_change_pct", 5.0)

    prices = fetch_crypto_prices()
    if not prices:
        return []

    alerts = []
    for coin, info in prices.items():
        change = info.get("usd_24h_change", 0)
        if change is None:
            continue
        if abs(change) >= pct_limit:
            direction = "📈" if change > 0 else "📉"
            alerts.append({
                "coin": coin,
                "price": info.get("usd", 0),
                "change_24h": round(change, 2),
                "direction": direction,
                "timestamp": datetime.now().isoformat(),
            })
    return alerts


def add_to_watchlist(coin_id):
    """Add a coin to the watchlist."""
    data = _load_market_data()
    if coin_id not in data["watchlist"]:
        data["watchlist"].append(coin_id)
        _save_market_data(data)
    return data["watchlist"]


def remove_from_watchlist(coin_id):
    """Remove a coin from the watchlist."""
    data = _load_market_data()
    if coin_id in data["watchlist"]:
        data["watchlist"].remove(coin_id)
        _save_market_data(data)
    return data["watchlist"]


def format_price_report(prices):
    """Format prices into a Telegram message."""
    if not prices:
        return "No price data available."

    msg = "*💰 Market Prices*\n\n"
    for coin, info in prices.items():
        price = info.get("usd", 0)
        change = info.get("usd_24h_change", 0) or 0
        mcap = info.get("usd_market_cap", 0) or 0
        direction = "🟢" if change >= 0 else "🔴"

        # Format price smartly
        if price >= 1:
            price_str = f"${price:,.2f}"
        else:
            price_str = f"${price:.6f}"

        mcap_str = ""
        if mcap > 1e9:
            mcap_str = f" | MCap: ${mcap/1e9:.1f}B"

        msg += f"{direction} *{coin.title()}*: {price_str} ({change:+.1f}%){mcap_str}\n"

    return msg


def format_alerts(alerts):
    """Format price alerts into a Telegram message."""
    if not alerts:
        return None

    msg = "*⚠️ Price Alerts*\n\n"
    for a in alerts:
        msg += f"{a['direction']} *{a['coin'].title()}*: ${a['price']:,.2f} ({a['change_24h']:+.1f}% 24h)\n"
    return msg


def format_trending(trending):
    """Format trending coins into a Telegram message."""
    if not trending:
        return "No trending data available."

    msg = "*🔥 Trending Coins*\n\n"
    for i, coin in enumerate(trending, 1):
        rank = f"#{coin['rank']}" if coin.get("rank") else "N/A"
        msg += f"{i}. *{coin['name']}* ({coin['symbol']}) — Rank {rank}\n"
    return msg
