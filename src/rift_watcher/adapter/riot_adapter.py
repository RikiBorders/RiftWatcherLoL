"""Riot adapter skeleton for Rift Watcher."""

import time
from datetime import datetime, timezone
from typing import List

from ..client.riot_api_client import RiotAPIClient
from ..client.database_client import DatabaseClient
from ..type.types import \
    InternalMatchRecord, \
    InternalPlayerProfile, \
    RiotMatchData, \
    RiotPlayerProfile, \
    InternalPlayerMatchPerformanceRecord
from ..constant.constant import UPDATE_PLAYER_MATCH_HISTORY_BATCH_SIZE, UPDATE_PLAYER_MATCH_HISTORY_JITTER_SECONDS

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
            "flex_rank": flex_rank,
        }

    def fetch_player_profile(self, game_name: str, tag_line: str, region: str) -> InternalPlayerProfile:
        """Fetch and translate player profile data from Riot."""
        raw_profile = self._riot_client.fetch_player_profile(game_name, tag_line, region)
        translated_profile = self.translate_player_profile(raw_profile)

        self._upsert_player_profile(translated_profile, game_name, tag_line, region)

        return translated_profile
    
    def get_recent_match_data(self, puuid: str, number_of_matches: int = 20, region: str = "NA") -> List[str]:
        """
        Get recent match IDs for a player.
        """
        match_ids = self._riot_client.get_match_ids(puuid=puuid, count=number_of_matches, region=region)

        match_data = self._riot_client.get_match_data_batch(match_ids, region)
        print(f"Fetched match data for {len(match_data)} matches for PUUID {puuid}")

        return match_data
        
    def update_matches_table(self):
        """
        Fetch recent matches for all players and update the database.

        TODO: As the number of players grows, we;'ll need to introduce caching, rate limiting, 
        and batch processing to avoid hitting Riot API limits and to keep the database up to date without excessive load.
        """
        player_profiles = self.database_client.get_all_players()
        for profile in player_profiles:
            puuid = profile.get("riot_puuid")
            if not puuid:
                print(f"Skipping profile with missing puuid: {profile}")
                continue

            try:
                matches = self.get_recent_match_data(
                    puuid, UPDATE_PLAYER_MATCH_HISTORY_BATCH_SIZE, profile.get("region")
                )
                for match in matches:
                    self.update_player_match_performance_table_with_match_data(match, puuid)
                    fields = self._extract_match_fields(match)

                    if not fields.get("riot_match_id"):
                        print(f"Skipping match with missing matchId: {match}")
                        continue

                    # Use upsert to avoid race conditions that can create
                    # duplicate match rows when multiple players reference
                    # the same Riot match concurrently.
                    payload = {
                        "riot_match_id": fields["riot_match_id"],
                        "queue_type": fields["queue_type"],
                        "patch_version": fields["patch_version"],
                        "game_duration_seconds": fields["game_duration_seconds"],
                        "started_at": fields["started_at"],
                        "region": profile.get("region"),
                        "game_end_timestamp": fields.get("game_end_timestamp"),
                        "platform_id": fields.get("platform_id"),
                    }

                    self.database_client.upsert_match(payload=payload)
                    time.sleep(UPDATE_PLAYER_MATCH_HISTORY_JITTER_SECONDS)

            except Exception as e:
                print(f"Error getting matches for {puuid}: {e}")

            time.sleep(UPDATE_PLAYER_MATCH_HISTORY_JITTER_SECONDS)

    def update_player_match_performance_table_with_match_data(self, match_data, puuid: str):
        payload = self._extract_player_match_performance(match_data, puuid)
        if payload:
            self.database_client.upsert_player_match_performance(payload)

    def get_player_match_performances_by_game_name(self, game_name: str, tag_line: str, region: str) -> InternalPlayerMatchPerformanceRecord:
        """Query the internal database to get performance data. A Riot API call is not made here."""
        puuid = self.database_client.get_player_puuid_by_game_name(game_name, tag_line, region)
        return self.get_player_match_performances_by_puuid(puuid)

    def get_player_match_performances_by_puuid(self, puuid: str) -> InternalPlayerMatchPerformanceRecord:
        return self.database_client.get_player_match_performances(puuid)

    def _extract_player_match_performance(self, match: dict, player_puuid: str) -> dict | None:
        """Extract a specific player's performance metrics from a match.
        
        Finds the participant with the given puuid and returns their performance data
        combined with match-level metadata.
        
        Returns None if the player is not found in the match.
        """
        # Extract match-level info
        riot_match_id = (match.get("metadata", {}) or {}).get("matchId")
        info = match.get("info", {}) or {}
        
        # Find the participant with matching puuid
        participants = info.get("participants", [])
        player_participant = None
        for participant in participants:
            if participant.get("puuid") == player_puuid:
                player_participant = participant
                break
        
        if not player_participant:
            print(f"Player with puuid {player_puuid} not found in match {riot_match_id}")
            return None
        
        # Extract player performance stats
        payload = {
            "match_id": riot_match_id,
            "puuid": player_puuid,
            "champion_id": player_participant.get("championId"),
            "champion_name": player_participant.get("championName"),
            "champion_experience": player_participant.get("champExperience"),
            "kills": player_participant.get("kills", 0),
            "deaths": player_participant.get("deaths", 0),
            "assists": player_participant.get("assists", 0),
            "gold_earned": player_participant.get("goldEarned", 0),
            "total_damage_dealt": player_participant.get("totalDamageDealt", 0),
            "total_damage_dealt_to_objectives": player_participant.get("damageDealtToObjectives"),
            "total_damage_dealt_to_champions": player_participant.get("totalDamageDealtToChampions", 0),
            "total_minions_killed": player_participant.get("totalMinionsKilled", 0),
            "role": player_participant.get("individualPosition", player_participant.get("role")),
            "team_id": player_participant.get("teamId"),
            "vision_score": player_participant.get("visionScore"),
            "win": player_participant.get("win", False),
        }
        
        return payload

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
        game_end_timestamp = info.get("gameEndTimestamp")
        platform_id = info.get("platformId")
        

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
            "game_end_timestamp": game_end_timestamp,
            "platform_id": platform_id,
        }
    
    def _resolve_queue_rank(self, queue_data: dict | None) -> tuple[str | None, str | None]:
        if not queue_data:
            return None, None

        return queue_data.get("tier"), queue_data.get("rank")

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

    def _format_rank_label(self, tier: str | None, division: str | None) -> str | None:
        if not tier or not division:
            return None

        return f"{tier.capitalize()} {division}"
