"""Shared typed models for Rift Watcher."""

from typing import Any, TypedDict

class RiotMatchData(TypedDict):
    game_id: str
    champion: str
    role: str
    kills: int
    deaths: int
    assists: int
    win: bool
    damage_share: float
    cs: int
    duration_minutes: int
    lp_change: int

class RiotPlayerProfile(TypedDict, total=False):
    puuid: str
    display_name: str
    region: str
    rank: str
    ranked_tier: str | None
    ranked_division: str | None
    solo_queue: dict[str, Any] | None
    flex_queue: dict[str, Any] | None

class InternalMatchRecord(TypedDict):
    game_id: str | None
    champion: str
    role: str
    kda: float
    win: bool
    damage_share: float
    cs_per_min: float
    lp_change: int

class InternalPlayerMatchPerformanceRecord(TypedDict):
    match_id: str | None
    puuid: int
    champion: str
    lp_change: int
    role: str
    kills: float
    deaths: float
    assists: float
    win: bool
    total_damage_dealt: float
    total_damage_dealt_to_champions: int
    total_lane_minions_killed: int

class InternalPlayerProfile(TypedDict):
    puuid: str | None
    display_name: str
    region: str
    rank: str
    flex_rank: str | None

class TrendStats(TypedDict):
    games_played: int
    average_kda: float
    average_cs_per_min: float
    win_rate: float
    trend_notes: str

class LPGraphPoint(TypedDict):
    game_index: int
    lp_total: int
    lp_change: int

class LifetimeLPStats(TypedDict):
    total_lp_change: int
    games: int
    lp_graph: list[LPGraphPoint]

PlayerOverview = dict[str, Any]
