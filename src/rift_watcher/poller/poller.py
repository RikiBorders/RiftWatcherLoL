"""Poller skeleton for periodic data refresh."""

import threading
import time
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any

from ..client.riot_api_client import RiotAPIClient
from ..client.database_client import DatabaseClient
from ..adapter.riot_adapter import RiotAdapter
from ..type.types import InternalPlayerProfile

class Poller:
    """Regularly polls the Riot API and updates stored player data."""

    def __init__(
        self,
        riot_client: RiotAPIClient,
        riot_adapter: RiotAdapter,
        database_client: DatabaseClient,
        interval_seconds: int = 7200,
        cache_size: int = 128,
    ):
        self.riot_client = riot_client
        self.riot_adapter = riot_adapter
        self.database_client = database_client
        self.interval_seconds = interval_seconds
        self.cache_size = cache_size
        self._player_cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        """Begin polling for fresh data."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop polling."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        """Poll player match data every interval and update the database."""
        while not self._stop_event.is_set():
            self.riot_adapter.update_matches_table()
            self._stop_event.wait(self.interval_seconds)
