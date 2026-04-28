"""Base adapter contract."""
from __future__ import annotations

import abc
import logging
from typing import List

from ..config import ScraperConfig
from ..http import HttpClient
from ..models import PropertyRecord

log = logging.getLogger(__name__)


class BaseAdapter(abc.ABC):
    """An adapter pulls candidate properties from a single source.

    Adapters MUST:
      * respect robots.txt (handled centrally by HttpClient)
      * never bypass authentication or paywalls
      * return raw candidates; filtering happens downstream
    """

    name: str = "base"

    def __init__(self, config: ScraperConfig, http: HttpClient) -> None:
        self.config = config
        self.http = http

    @abc.abstractmethod
    def fetch(self) -> List[PropertyRecord]:
        ...

    def _log_count(self, records: List[PropertyRecord]) -> None:
        log.info("[%s] returned %d candidate(s)", self.name, len(records))
