"""Crypto and market price tracker with trading signals."""

import json
import urllib.request
import os
import logging
from datetime import datetime

log = logging.getLogger("market")

MARKET_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "market_data.json")

DEFAULT_WATCHLIST = ["bitcoin", "ethereum", "solana"]
DEFAULT_ALERT_THRESHOLDS = {
    "price_change_pct": 5.0,
    "volume_spike_pct": 50.0,
}


def _load_market_data():
    if os.path.exists(MARKET_FILE):
        try:
            with open(MARKET_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "watchlist": DEFAULT_WATCHLIST,
        "alert_thresholds": DEFAULT_ALERT_THRESHOLDS,
        "price_history": [],
        "alerts_sent": [],
    }


def _save_market_data(data):
    with open(MARKET_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _format_mcap(mcap):
    """Format market cap with appropriate unit."""
    if mcap >= 1e12:
        return f"${mcap/1e12:.1f}T"
    elif mcap >= 1e9:
        return f"${mcap/1e9:.1f}B"
    elif mcap >= 1e6:
        return f"${mcap/1e6:.1f}M"
    return f"${mcap:,.0f}"


def fetch_crypto_prices(coins=None):
    """Fetch current crypto prices from CoinGecko free API."""
    data = _load_market_data()
    if coins is None:
        coins = data.get("watchlist", DEFAULT_WATCHLIST)

    ids = ",".join(coins)
    url = (
        f"https://api.coingecko.com/api/v3/simple/price?ids={ids}"
        f"&vs_currencies=usd&include_24hr_change=true"
        f"&include_market_cap=true&include_24hr_vol=true"
    )

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
        data["price_history"] = data["price_history"][-200:]
        _save_market_data(data)
        return prices
    except Exception as e:
        log.warning("Price fetch error: %s", e)
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
        log.warning("Trending fetch error: %s", e)
        return []


def calculate_signals():
    """Calculate trading signals from price history."""
    data = _load_market_data()
    history = data.get("price_history", [])

    if len(history) < 5:
        return {}

    signals = {}
    # Get unique coins from latest snapshot
    latest = history[-1].get("prices", {})

    for coin in latest:
        # Collect price series for this coin
        prices = []
        for snap in history[-48:]:  # Last ~24 hours of 30-min snapshots
            p = snap.get("prices", {}).get(coin, {})
            if p and "usd" in p:
                prices.append(p["usd"])

        if len(prices) < 5:
            continue

        current = prices[-1]
        coin_signals = {
            "price": current,
            "signals": [],
        }

        # --- Momentum: compare current vs moving average ---
        ma_short = sum(prices[-6:]) / min(len(prices[-6:]), 6)   # ~3hr MA
        ma_long = sum(prices[-24:]) / min(len(prices[-24:]), 24) # ~12hr MA

        if ma_short > ma_long * 1.02:
            coin_signals["signals"].append("📈 Bullish momentum (short MA > long MA)")
            coin_signals["trend"] = "bullish"
        elif ma_short < ma_long * 0.98:
            coin_signals["signals"].append("📉 Bearish momentum (short MA < long MA)")
            coin_signals["trend"] = "bearish"
        else:
            coin_signals["trend"] = "neutral"

        # --- RSI approximation (14-period) ---
        if len(prices) >= 15:
            gains = []
            losses = []
            for i in range(1, min(15, len(prices))):
                change = prices[-i] - prices[-(i+1)]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))

            avg_gain = sum(gains) / 14 if gains else 0.001
            avg_loss = sum(losses) / 14 if losses else 0.001
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            coin_signals["rsi"] = round(rsi, 1)

            if rsi < 30:
                coin_signals["signals"].append(f"🟢 RSI {rsi:.0f} — Oversold (buy signal)")
            elif rsi > 70:
                coin_signals["signals"].append(f"🔴 RSI {rsi:.0f} — Overbought (sell signal)")

        # --- Price velocity (rate of change) ---
        if len(prices) >= 3:
            velocity = ((prices[-1] - prices[-3]) / prices[-3]) * 100
            coin_signals["velocity"] = round(velocity, 2)
            if abs(velocity) > 3:
                direction = "surging" if velocity > 0 else "dumping"
                coin_signals["signals"].append(f"⚡ {direction} ({velocity:+.1f}% in ~1.5hr)")

        # --- Volume spike ---
        vol_current = latest.get(coin, {}).get("usd_24h_vol", 0)
        # Compare with historical average
        vols = []
        for snap in history[-48:]:
            v = snap.get("prices", {}).get(coin, {}).get("usd_24h_vol", 0)
            if v:
                vols.append(v)
        if vols and vol_current:
            avg_vol = sum(vols) / len(vols)
            if avg_vol > 0 and vol_current > avg_vol * 1.5:
                spike_pct = ((vol_current - avg_vol) / avg_vol) * 100
                coin_signals["signals"].append(f"🔊 Volume spike +{spike_pct:.0f}%")

        if coin_signals["signals"]:
            signals[coin] = coin_signals

    return signals


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

    # Also check for trading signals
    signals = calculate_signals()
    for coin, sig in signals.items():
        if sig.get("signals"):
            alerts.append({
                "coin": coin,
                "price": sig.get("price", 0),
                "change_24h": 0,
                "direction": "📊",
                "signals": sig["signals"],
                "rsi": sig.get("rsi"),
                "trend": sig.get("trend"),
                "timestamp": datetime.now().isoformat(),
            })

    return alerts


def add_to_watchlist(coin_id):
    data = _load_market_data()
    if coin_id not in data["watchlist"]:
        data["watchlist"].append(coin_id)
        _save_market_data(data)
    return data["watchlist"]


def remove_from_watchlist(coin_id):
    data = _load_market_data()
    if coin_id in data["watchlist"]:
        data["watchlist"].remove(coin_id)
        _save_market_data(data)
    return data["watchlist"]


def format_price_report(prices):
    """Format prices into a Telegram message with signals."""
    if not prices:
        return "No price data available."

    msg = "*💰 Market Prices*\n\n"
    for coin, info in prices.items():
        price = info.get("usd", 0)
        change = info.get("usd_24h_change", 0) or 0
        mcap = info.get("usd_market_cap", 0) or 0
        vol = info.get("usd_24h_vol", 0) or 0
        direction = "🟢" if change >= 0 else "🔴"

        if price >= 1:
            price_str = f"${price:,.2f}"
        else:
            price_str = f"${price:.6f}"

        mcap_str = f" | MCap: {_format_mcap(mcap)}" if mcap else ""
        vol_str = f" | Vol: {_format_mcap(vol)}" if vol else ""

        msg += f"{direction} *{coin.title()}*: {price_str} ({change:+.1f}%){mcap_str}{vol_str}\n"

    # Add signals if available
    signals = calculate_signals()
    if signals:
        msg += "\n*📊 Trading Signals*\n"
        for coin, sig in signals.items():
            for s in sig["signals"][:2]:
                msg += f"  {coin.title()}: {s}\n"

    return msg


def format_alerts(alerts):
    if not alerts:
        return None

    msg = "*⚠️ Market Alerts*\n\n"
    for a in alerts:
        if a.get("signals"):
            msg += f"*{a['coin'].title()}* (${a['price']:,.2f})\n"
            for s in a["signals"][:3]:
                msg += f"  {s}\n"
        elif a.get("change_24h"):
            msg += f"{a['direction']} *{a['coin'].title()}*: ${a['price']:,.2f} ({a['change_24h']:+.1f}% 24h)\n"
    return msg


def format_trending(trending):
    if not trending:
        return "No trending data available."

    msg = "*🔥 Trending Coins*\n\n"
    for i, coin in enumerate(trending, 1):
        rank = f"#{coin['rank']}" if coin.get("rank") else "N/A"
        msg += f"{i}. *{coin['name']}* ({coin['symbol']}) — Rank {rank}\n"
    return msg
