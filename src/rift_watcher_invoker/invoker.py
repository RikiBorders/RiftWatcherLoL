"""Simple invoker for Rift Watcher API endpoints.

This module is intentionally minimal so you can call API endpoints
directly with dummy inputs that are easy to replace.
"""

from typing import Any

from rift_watcher.api.rift_watcher_api import RiftWatcherAPI
from rift_watcher.client.riot_api_client import RiotAPIClient
from rift_watcher.adapter.riot_adapter import RiotAdapter
from rift_watcher.player_facade import PlayerFacade
from rift_watcher.api.rift_watcher_api import RiftWatcherAPI

class Invoker:
    """Simple API invoker for Rift Watcher endpoints."""

    def __init__(self, api: RiftWatcherAPI) -> None:
        self.api = api

    def player_overview(self, summoner_name: str, region: str) -> Any:
        """Call the player overview endpoint."""
        return self.api.get_player_overview(summoner_name, region)


riot_client = RiotAPIClient(region="NA")
riot_adapter = RiotAdapter(database_client=None, riot_client=riot_client)
player_facade = PlayerFacade(riot_adapter, stat_calculator=...)

api = RiftWatcherAPI(player_facade)
invoker = Invoker(api)
overview = invoker.player_overview("Rik Astley", "NA")
print(overview)
