"""REST API layer skeleton for Rift Watcher."""

from ..player_facade import PlayerFacade
from ..types import PlayerOverview

class RiftWatcherAPI:
    """API layer exposing Rift Watcher endpoints."""

    def __init__(self, player_facade: PlayerFacade):
        self.player_facade = player_facade

    def get_player_overview(self, game_name: str, tag_line: str, region: str) -> PlayerOverview:
        """
            Retrieve data to provide a player overview. 
            Data includes 
            1. username
            2. rank
            3. region
        """
        try:
            return self.player_facade.get_player_overview(game_name, tag_line, region)
        except Exception as e:
            # Placeholder: Implement proper error handling and logging.
            print(f"Error fetching player overview for {game_name}#{tag_line} in {region}: {e}")
            raise
