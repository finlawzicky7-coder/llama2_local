"""HTTP client with retries, throttling, and robots.txt enforcement."""
from __future__ import annotations

import logging
import threading
import time
from typing import Dict, Optional
from urllib import robotparser
from urllib.parse import urlparse

import requests

log = logging.getLogger(__name__)


class RobotsCache:
    """Cache RobotFileParser per-host so we only fetch /robots.txt once each.

    We fetch robots.txt with the same user agent used for content requests
    so Cloudflare / WAF rules don't reject the bare-stdlib opener (which
    has no UA and gets 403'd, causing urllib's robotparser to set
    disallow_all=True).
    """

    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent
        self._cache: Dict[str, robotparser.RobotFileParser | object] = {}
        self._lock = threading.Lock()
        # Sentinel meaning "we tried and the host has no usable robots.txt".
        self._ALLOW_ALL = object()

    def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        with self._lock:
            rp = self._cache.get(host)
            if rp is None:
                rp = self._load(host)
                self._cache[host] = rp
        if rp is self._ALLOW_ALL:
            return True
        if rp is None:
            return False
        return rp.can_fetch(self.user_agent, url)

    def _load(self, host: str):
        try:
            resp = requests.get(
                host + "/robots.txt",
                headers={"User-Agent": self.user_agent},
                timeout=10,
            )
        except Exception as exc:
            log.warning("robots.txt fetch error for %s (%s) — defaulting to disallow",
                        host, exc)
            return None

        # 404 / 410 => no robots.txt => everything allowed (RFC 9309).
        if resp.status_code in (404, 410):
            return self._ALLOW_ALL
        # Some hosts (Cloudflare/Akamai) block /robots.txt with 403. RFC 9309
        # leaves this as "implementation-defined"; we treat it as no-robots
        # because the server itself is refusing to publish a policy.
        if resp.status_code == 403:
            log.info("robots.txt 403 for %s — treating as no-robots-policy", host)
            return self._ALLOW_ALL
        if resp.status_code >= 400:
            log.warning("robots.txt HTTP %d for %s — defaulting to disallow",
                        resp.status_code, host)
            return None

        rp = robotparser.RobotFileParser()
        rp.parse(resp.text.splitlines())
        return rp


class HttpClient:
    """Thin requests wrapper with retry, throttle, and robots check."""

    def __init__(
        self,
        user_agent: str,
        timeout: float = 20.0,
        retries: int = 3,
        backoff: float = 2.0,
        throttle: float = 1.0,
    ) -> None:
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.throttle = throttle
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.robots = RobotsCache(user_agent)
        self._last_request_at: Dict[str, float] = {}
        self._throttle_lock = threading.Lock()

    def _throttle(self, url: str) -> None:
        host = urlparse(url).netloc
        with self._throttle_lock:
            last = self._last_request_at.get(host, 0.0)
            now = time.time()
            wait = self.throttle - (now - last)
            if wait > 0:
                time.sleep(wait)
            self._last_request_at[host] = time.time()

    def get(self, url: str, params: Optional[dict] = None) -> Optional[requests.Response]:
        if not self.robots.allowed(url):
            log.warning("robots.txt disallows %s — skipping", url)
            return None
        self._throttle(url)

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code in (429, 503):
                    raise requests.RequestException(f"transient {resp.status_code}")
                resp.raise_for_status()
                return resp
            except Exception as exc:
                last_exc = exc
                wait = self.backoff * (2 ** (attempt - 1))
                log.warning("GET %s failed (attempt %d/%d): %s — retrying in %.1fs",
                            url, attempt, self.retries, exc, wait)
                time.sleep(wait)
        log.error("GET %s permanently failed: %s", url, last_exc)
        return None
