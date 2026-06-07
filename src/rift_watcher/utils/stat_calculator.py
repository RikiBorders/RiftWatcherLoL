"""Stat calculator skeleton for Rift Watcher."""

from statistics import mean
from typing import List

from ..client.database_client import DatabaseClient
from ..adapter.riot_adapter import RiotAdapter
from ..type.types import LPGraphPoint, LifetimeLPStats, TrendStats

class StatCalculator:
    """Performs calculations on player and match data."""

    def __init__(self, database_client: DatabaseClient, riot_adapter: RiotAdapter | None = None):
        self.database_client = database_client
        self.riot_adapter = riot_adapter

    def calculate_trends(self, puuid: str) -> TrendStats:
        """Calculate long-term trends for a player."""
        matches = self.database_client.get_player_match_history(puuid)
        if not matches:
            return {
                "games_played": 0,
                "average_kda": 0.0,
                "average_cs_per_min": 0.0,
                "win_rate": 0.0,
                "trend_notes": "Placeholder: use rolling windows or regression for trend detection.",
            }

        kdas = [match.get("kda", 0.0) for match in matches]
        cs_rates = [match.get("cs_per_min", 0.0) for match in matches]
        wins = sum(1 for match in matches if match.get("win"))

        return {
            "games_played": len(matches),
            "average_kda": round(mean(kdas), 2),
            "average_cs_per_min": round(mean(cs_rates), 2),
            "win_rate": round(wins / len(matches), 4),
            "trend_notes": "Placeholder: use rolling windows or regression for trend detection.",
        }

    def calculate_lifetime_lp(self, puuid: str) -> LifetimeLPStats:
        """Calculate lifetime LP gain/loss over a sequence of games."""
        matches = self.database_client.get_player_match_history(puuid)
        if not matches:
            return {
                "total_lp_change": 0,
                "games": 0,
                "lp_graph": [],
            }

        total_lp = 0
        timeline: List[LPGraphPoint] = []
        for idx, match in enumerate(matches, start=1):
            lp_change = match.get("lp_change", 0)
            total_lp += lp_change
            timeline.append({"game_index": idx, "lp_total": total_lp, "lp_change": lp_change})

        return {
            "total_lp_change": total_lp,
            "games": len(matches),
            "lp_graph": timeline,
        }
