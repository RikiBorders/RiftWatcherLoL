"""Riot adapter skeleton for Rift Watcher."""

from ..client.riot_api_client import RiotAPIClient
from ..client.database_client import DatabaseClient
from ..types import InternalMatchRecord, InternalPlayerProfile, RiotMatchData, RiotPlayerProfile

class RiotAdapter:
    """Translates Riot API and database responses into internal models."""

    def __init__(self, database_client: DatabaseClient, riot_client: RiotAPIClient):
        self.database_client = database_client
        self._riot_client = riot_client

    def translate_match_data(self, raw_match_data: list[RiotMatchData]) -> list[InternalMatchRecord]:
        """Normalize raw match data into internal representation."""
        translated: list[InternalMatchRecord] = []
        for match in raw_match_data:
            kills = match.get("kills", 0)
            deaths = match.get("deaths", 0)
            assists = match.get("assists", 0)
            duration = match.get("duration_minutes", 1)
            kda = (kills + assists) / max(deaths, 1)
            translated.append(
                {
                    "game_id": match.get("game_id"),
                    "champion": match.get("champion", "Unknown"),
                    "role": match.get("role", "Unknown"),
                    "kda": round(kda, 2),
                    "win": bool(match.get("win", False)),
                    "damage_share": float(match.get("damage_share", 0.0)),
                    "cs_per_min": round(match.get("cs", 0) / max(duration, 1), 2),
                    "lp_change": match.get("lp_change", 0),
                    # Placeholder: Add additional fields for the database schema as needed.
                }
            )
        return translated

    def translate_player_profile(self, raw_profile_data: RiotPlayerProfile) -> InternalPlayerProfile:
        """Normalize raw player profile data into internal representation."""
        return {
            "player_id": raw_profile_data.get("player_id"),
            "display_name": raw_profile_data.get("display_name", "Unknown"),
            "region": raw_profile_data.get("region", self._riot_client.region),
            "rank": raw_profile_data.get("rank", "Unranked"),
            "ranked_tier": raw_profile_data.get("ranked_tier"),
            "ranked_division": raw_profile_data.get("ranked_division"),
            # Placeholder: Extend profile translation with additional Riot fields.
        }

    def fetch_player_profile(self, summoner_name: str, region: str) -> InternalPlayerProfile:
        """Fetch and translate player profile data from Riot."""
        raw_profile = self._riot_client.fetch_player_profile(summoner_name, region)
        return self.translate_player_profile(raw_profile)
