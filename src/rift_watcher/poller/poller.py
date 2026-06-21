"""Poller skeleton for periodic data refresh."""

import threading
import logging
import time
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any


from ..client.riot_api_client import RiotAPIClient
from ..client.database_client import DatabaseClient
from ..adapter.riot_adapter import RiotAdapter
from ..type.types import InternalPlayerProfile

logger = logging.getLogger(__name__)

class Poller:
    """Regularly polls the Riot API and updates stored player data."""

    def __init__(
        self,
        riot_adapter: RiotAdapter,
        interval_seconds: int = 1800,
    ):
        self.riot_adapter = riot_adapter
        self.interval_seconds = interval_seconds
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
            logger.info("Poller: Completed update_matches_table at %s", datetime.now(timezone.utc).isoformat())
            self._stop_event.wait(self.interval_seconds)
