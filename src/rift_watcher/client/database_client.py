"""Database client skeleton for Rift Watcher."""

from __future__ import annotations

import os
from typing import Any, Optional

try:  # prefer the real supabase package when available
    from supabase import create_client, Client  # type: ignore
except Exception:  # pragma: no cover - fallback for test shim
    from tests.supabase import Client, create_client

from ..type.types import (
    InternalMatchRecord,
    InternalPlayerProfile,
)

class DatabaseClient:
    """Encapsulates all Supabase database interactions."""
    PLAYERS_TABLE = "players"
    MATCHES_TABLE = "matches"
    PLAYER_MATCH_PERFORMANCE_TABLE = "player_match_performance"

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ) -> None:
        self._client: Client = create_client(
            supabase_url or os.environ["SUPABASE_URL"],
            supabase_key or os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )

    @property
    def client(self) -> Client:
        """Expose raw Supabase client when needed."""
        return self._client


    # ============================================================
    # PLAYERS
    # ============================================================

    def get_player_by_puuid(
        self,
        riot_puuid: str,
    ) -> Optional[dict]:
        """Fetch a player by Riot PUUID."""
        response = (
            self._client.table(self.PLAYERS_TABLE)
            .select("*")
            .eq("riot_puuid", riot_puuid)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def get_player_by_id(
        self,
        player_id: str,
    ) -> Optional[dict]:
        """Fetch a player by UUID."""
        response = (
            self._client.table(self.PLAYERS_TABLE)
            .select("*")
            .eq("id", player_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def create_player(
        self,
        riot_puuid: str,
        summoner_name: str,
        tagline: str,
        region: str,
        current_rank: str | None = None,
    ) -> dict:
        """Create a player record."""

        payload = {
            "riot_puuid": riot_puuid,
            "summoner_name": summoner_name,
            "tagline": tagline,
            "region": region,
            "current_rank": current_rank,
        }
        response = (
            self._client.table(self.PLAYERS_TABLE)
            .insert(payload)
            .execute()
        )

        return response.data[0]

    def upsert_player(
        self,
        riot_puuid: str,
        summoner_name: str,
        tagline: str,
        region: str,
        current_rank: str | None = None,
    ) -> dict:
        """
        Create or update a player using riot_puuid
        as the unique identifier.
        """

        payload = {
            "riot_puuid": riot_puuid,
            "summoner_name": summoner_name,
            "tagline": tagline,
            "region": region,
            "current_rank": current_rank,
        }
        response = (
            self._client.table(self.PLAYERS_TABLE)
            .upsert(
                payload,
                on_conflict="riot_puuid",
            )
            .execute()
        )

        return response.data[0]

    def update_player_rank(
        self,
        riot_puuid: str,
        current_rank: str,
    ) -> dict:
        """Update only the player's rank."""
        response = (
            self._client.table(self.PLAYERS_TABLE)
            .update(
                {
                    "current_rank": current_rank,
                }
            )
            .eq("riot_puuid", riot_puuid)
            .execute()
        )

        return response.data[0]

    def update_player_identity(
        self,
        riot_puuid: str,
        summoner_name: str,
        tagline: str,
    ) -> dict:
        """Update Riot name/tag combination."""
        response = (
            self._client.table(self.PLAYERS_TABLE)
            .update(
                {
                    "summoner_name": summoner_name,
                    "tagline": tagline,
                }
            )
            .eq("riot_puuid", riot_puuid)
            .execute()
        )

        return response.data[0]

    def delete_player(
        self,
        riot_puuid: str,
    ) -> None:
        """Delete player record."""
        (
            self._client.table(self.PLAYERS_TABLE)
            .delete()
            .eq("riot_puuid", riot_puuid)
            .execute()
        )

    # ============================================================
    # PLAYER MATCH PERFORMANCE
    # ============================================================

    def get_player_match_performance(
        self,
        player_id: str,
        match_id: str,
    ) -> dict | None:
        """
        Get a player's stats for a specific match.
        """

        response = (
            self._client.table(self.PLAYER_MATCH_PERFORMANCE_TABLE)
            .select("*")
            .eq("player_id", player_id)
            .eq("match_id", match_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def create_player_match_performance(
        self,
        *,
        player_id: str,
        match_id: str,
        champion: str,
        role: str,
        kills: int,
        deaths: int,
        assists: int,
        kda_ratio: float,
        win: bool,
        damage_share: float,
        cs_per_min: float,
    ) -> dict:
        """
        Insert a match performance record.
        """
        payload = {
            "player_id": player_id,
            "match_id": match_id,
            "champion": champion,
            "role": role,
            "kills": kills,
            "deaths": deaths,
            "assists": assists,
            "kda_ratio": kda_ratio,
            "win": win,
            "damage_share": damage_share,
            "cs_per_min": cs_per_min,
        }

        response = (
            self._client.table(self.PLAYER_MATCH_PERFORMANCE_TABLE)
            .insert(payload)
            .execute()
        )

        return response.data[0]

    def upsert_player_match_performance(
        self,
        payload: dict,
    ) -> dict:
        """
        Upsert player match performance record.

        Assumes unique(player_id, match_id).
        """
        response = (
            self._client.table(self.PLAYER_MATCH_PERFORMANCE_TABLE)
            .upsert(
                payload,
                on_conflict="player_id,match_id",
            )
            .execute()
        )

        return response.data[0]

    def bulk_upsert_player_match_performance(
        self,
        records: list[dict],
    ) -> list[dict]:
        """
        Bulk ingest player match performance records.
        """
        if not records:
            return []

        response = (
            self._client.table(self.PLAYER_MATCH_PERFORMANCE_TABLE)
            .upsert(
                records,
                on_conflict="player_id,match_id",
            )
            .execute()
        )

        return response.data

    def delete_player_match_performance(
        self,
        player_id: str,
        match_id: str,
    ) -> None:
        """
        Delete a player's match record.
        """
        (
            self._client.table(self.PLAYER_MATCH_PERFORMANCE_TABLE)
            .delete()
            .eq("player_id", player_id)
            .eq("match_id", match_id)
            .execute()
        )

    # ============================================================
    # MACTHES
    # ============================================================

    def get_match_by_id(
        self,
        match_id: str,
    ) -> dict | None:
        """
        Fetch a match by internal UUID.
        """

        response = (
            self._client.table(self.MATCHES_TABLE)
            .select("*")
            .eq("id", match_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def get_match_by_riot_match_id(
        self,
        riot_match_id: str,
    ) -> dict | None:
        """
        Fetch a match by Riot match ID.
        """

        response = (
            self._client.table(self.MATCHES_TABLE)
            .select("*")
            .eq("riot_match_id", riot_match_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]
    
    def create_match(
        self,
        riot_match_id: str,
        queue_type: str,
        patch_version: str,
        game_duration_seconds: int,
        started_at: str,
    ) -> dict:
        """
        Create a match record.
        """

        payload = {
            "riot_match_id": riot_match_id,
            "queue_type": queue_type,
            "patch_version": patch_version,
            "game_duration_seconds": game_duration_seconds,
            "started_at": started_at,
        }

        response = (
            self._client.table(self.MATCHES_TABLE)
            .insert(payload)
            .execute()
        )

        return response.data[0]
    
    def upsert_match(
        self,
        payload: dict,
    ) -> dict:
        """
        Create or update a match.
        """

        response = (
            self._client.table(self.MATCHES_TABLE)
            .upsert(
                payload,
                on_conflict="riot_match_id",
            )
            .execute()
        )

        return response.data[0]
    
    def bulk_upsert_matches(
        self,
        matches: list[dict],
    ) -> list[dict]:
        """
        Bulk create/update match records.
        """

        if not matches:
            return []

        response = (
            self._client.table(self.MATCHES_TABLE)
            .upsert(
                matches,
                on_conflict="riot_match_id",
            )
            .execute()
        )

        return response.data

    def delete_match(
        self,
        riot_match_id: str,
    ) -> None:
        """
        Delete a match.
        """

        (
            self._client.table(self.MATCHES_TABLE)
            .delete()
            .eq("riot_match_id", riot_match_id)
            .execute()
        )

    def match_exists(
        self,
        riot_match_id: str,
    ) -> bool:
        """
        Check whether a match already exists.
        """

        response = (
            self._client.table(self.MATCHES_TABLE)
            .select("id")
            .eq("riot_match_id", riot_match_id)
            .limit(1)
            .execute()
        )

        return bool(response.data)