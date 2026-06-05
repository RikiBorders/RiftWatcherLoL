"""Poller skeleton for periodic data refresh."""

import threading
import time
from collections import OrderedDict
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
        self._load_player_cache()
        while not self._stop_event.is_set():
            usernames = list(self._player_cache.keys())
            for username in usernames:
                if self._stop_event.is_set():
                    break
                raw_matches = self.riot_client.fetch_match_history(username)
                processed = self.riot_adapter.translate_match_data(raw_matches)
                for match in processed:
                    self.database_client.upsert_match_record(username, match)
                # Refresh cache entry after updating data
                self._touch_cache(username)
            self._stop_event.wait(self.interval_seconds)

    def _load_player_cache(self) -> None:
        """Seed the local LRU cache from the database at startup."""
        cached_usernames = self.database_client.fetch_all_cached_player_usernames()
        for username in cached_usernames:
            profile = self.database_client.get_cached_player_profile(username) or {}
            self._player_cache[username] = profile
            if len(self._player_cache) > self.cache_size:
                self._player_cache.popitem(last=False)

    def _touch_cache(self, username: str) -> None:
        """Update cache ordering and ensure player is present."""
        profile = self._player_cache.pop(username, None)
        if profile is None:
            profile = self.database_client.get_cached_player_profile(username) or {}
        self._player_cache[username] = profile
        while len(self._player_cache) > self.cache_size:
            self._player_cache.popitem(last=False)

    def get_cached_player_data(self, username: str) -> InternalPlayerProfile | None:
        """Return cached player data or refresh from the database as needed."""
        if username in self._player_cache:
            self._touch_cache(username)
            return self._player_cache[username]

        profile = self.database_client.get_cached_player_profile(username)
        if profile:
            self._player_cache[username] = profile
            if len(self._player_cache) > self.cache_size:
                self._player_cache.popitem(last=False)
        return profile
