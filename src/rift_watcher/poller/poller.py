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

    def _extract_match_fields(self, match: dict) -> dict:
        """Extract DB-ready fields from a Riot match payload.

        Returns a dict suitable for `DatabaseClient.create_match`.
        """
        riot_match_id = (match.get("metadata", {}) or {}).get("matchId")
        info = match.get("info", {}) or {}
        queue_type = info.get("gameMode")
        patch_version = info.get("gameVersion")
        game_duration_seconds = info.get("gameDuration")
        started_at_ts = info.get("gameStartTimestamp")

        started_at = None
        if isinstance(started_at_ts, (int, float)):
            try:
                started_at = datetime.fromtimestamp(
                    started_at_ts / 1000.0, tz=timezone.utc
                ).isoformat()
            except Exception:
                started_at = None

        return {
            "riot_match_id": riot_match_id,
            "queue_type": queue_type,
            "patch_version": patch_version,
            "game_duration_seconds": game_duration_seconds,
            "started_at": started_at,
        }

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
            player_profiles = self.database_client.fetch_all_player_profiles()
            for profile in player_profiles:
                puuid = profile.get("riot_puuid")
                if not puuid:
                    print(f"Skipping profile with missing puuid: {profile}")
                    continue

                try:
                    matches = self.riot_adapter.get_recent_match_data(
                        puuid, 5, profile.get("region", "NA")
                    )
                    for match in matches:
                        fields = self._extract_match_fields(match)

                        if not fields.get("riot_match_id"):
                            print(f"Skipping match with missing matchId: {match}")
                            continue

                        try:
                            self.database_client.create_match(
                                riot_match_id=fields["riot_match_id"],
                                queue_type=fields["queue_type"],
                                patch_version=fields["patch_version"],
                                game_duration_seconds=fields["game_duration_seconds"],
                                started_at=fields["started_at"],
                            )
                        except TypeError:
                            # Fallback to positional call for older signatures
                            self.database_client.create_match(
                                fields["riot_match_id"],
                                fields["queue_type"],
                                fields["patch_version"],
                                fields["game_duration_seconds"],
                                fields["started_at"],
                            )
                except Exception as e:
                    print(f"Error getting matches for {puuid}: {e}")

            self._stop_event.wait(self.interval_seconds)

        return profile
