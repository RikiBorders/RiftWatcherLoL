"""Riot adapter skeleton for Rift Watcher."""

from typing import List

from ..client.riot_api_client import RiotAPIClient
from ..client.database_client import DatabaseClient
from ..type.types import InternalMatchRecord, InternalPlayerProfile, RiotMatchData, RiotPlayerProfile

class RiotAdapter:
    """Translates Riot API and database responses into internal models."""

    def __init__(self, database_client: DatabaseClient | None, riot_client: RiotAPIClient):
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
        solo_tier, solo_division = self._resolve_queue_rank(raw_profile_data.get("solo_queue"))
        flex_tier, flex_division = self._resolve_queue_rank(raw_profile_data.get("flex_queue"))

        solo_rank = self._format_rank_label(solo_tier, solo_division) or "Unranked"
        flex_rank = self._format_rank_label(flex_tier, flex_division) or "Unranked"

        return {
            "puuid": raw_profile_data.get("puuid"),
            "display_name": raw_profile_data.get("display_name", "Unknown"),
            "region": raw_profile_data.get("region", self._riot_client.region),
            "rank": solo_rank,
            "ranked_tier": solo_tier,
            "ranked_division": solo_division,
            "flex_rank": flex_rank,
            "flex_ranked_division": flex_division,
        }

    def fetch_player_profile(self, game_name: str, tag_line: str, region: str) -> InternalPlayerProfile:
        """Fetch and translate player profile data from Riot."""
        raw_profile = self._riot_client.fetch_player_profile(game_name, tag_line, region)
        translated_profile = self.translate_player_profile(raw_profile)

        self._upsert_player_profile(translated_profile, game_name, tag_line, region)

        return translated_profile
    
    def _upsert_player_profile(
        self,
        translated_profile: InternalPlayerProfile,
        game_name: str,
        tag_line: str,
        region: str,
    ) -> None:
        """Persist player metadata in the database, using UNRANKED when needed.

        This is a no-op when the adapter was created without a database client.
        """
        solo_rank = translated_profile.get("rank")
        flex_rank = translated_profile.get("flex_rank")

        print(f"Upserting player profile for {translated_profile['display_name']} with puuid {translated_profile['puuid']} and solo rank {solo_rank} and flex rank {flex_rank}")

        self.database_client.upsert_player(
            translated_profile.get("puuid"),
            game_name,
            tag_line,
            region,
            solo_rank or "UNRANKED",
            flex_rank or "UNRANKED",
        )

    def get_recent_player_matches(self, puuid: str, number_of_matches: int) -> list[InternalMatchRecord]:
        match_ids = self.get_match_ids( puuid=puuid, number_of_matches=number_of_matches)
        
        if not match_ids:
            print(f"No matches found for PUUID: {puuid}")
            return []
            

    def get_recent_match_data(self, puuid: str, number_of_matches: int = 20, region: str = "NA") -> List[str]:
        """
        Get recent match IDs for a player.
        """
        match_ids = self._riot_client.get_match_ids(puuid=puuid, number_of_matches=number_of_matches, region=region)

        match_data = self._riot_client.get_match_data_batch(match_ids)
        print(f"Fetched match data for {len(match_data)} matches for PUUID {puuid}")

        return match_data
        
    def _resolve_queue_rank(self, queue_data: dict | None) -> tuple[str | None, str | None]:
        if not queue_data:
            return None, None

        return queue_data.get("tier"), queue_data.get("rank")

    def _format_rank_label(self, tier: str | None, division: str | None) -> str | None:
        if not tier or not division:
            return None

        return f"{tier.title()} {division}"
