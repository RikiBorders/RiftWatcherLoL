"""Player facade skeleton for Rift Watcher."""

from .adapter.riot_adapter import RiotAdapter
from .stat_calculator import StatCalculator
from .types import PlayerOverview

class PlayerFacade:
    """Facade to simplify player-related operations for the API layer."""

    def __init__(self, riot_adapter: RiotAdapter, stat_calculator: StatCalculator):
        self.riot_adapter = riot_adapter
        self.stat_calculator = stat_calculator

    def get_player_overview(self, game_name: str, tag_line: str, region: str) -> PlayerOverview:
        """Compile player overview data for API consumption."""
        return self.riot_adapter.fetch_player_profile(game_name, tag_line, region)

