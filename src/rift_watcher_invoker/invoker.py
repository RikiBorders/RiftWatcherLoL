"""Simple invoker for Rift Watcher API endpoints.

This module is intentionally minimal so you can call API endpoints
directly with dummy inputs that are easy to replace.
"""

import os
from typing import Any

from rift_watcher.api.rift_watcher_api import RiftWatcherAPI
from rift_watcher.client.riot_api_client import RiotAPIClient
from rift_watcher.adapter.riot_adapter import RiotAdapter
from rift_watcher.facade.player_facade import PlayerFacade
from rift_watcher.api.rift_watcher_api import RiftWatcherAPI
from rift_watcher.client.database_client import DatabaseClient


class Invoker:
    """Simple API invoker for Rift Watcher endpoints."""

    def __init__(self, api: RiftWatcherAPI) -> None:
        self.api = api

    def player_overview(self, game_name: str, tag_line: str, region: str) -> Any:
        """Call the player overview endpoint."""
        return self.api.get_player_overview(game_name, tag_line, region)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
db_client = DatabaseClient(supabase_url=supabase_url, supabase_key=supabase_key)

riot_client = RiotAPIClient(region="NA")
riot_adapter = RiotAdapter(database_client=db_client, riot_client=riot_client)
player_facade = PlayerFacade(riot_adapter, stat_calculator=...)

api = RiftWatcherAPI(player_facade)
invoker = Invoker(api)


overview = invoker.player_overview("Rik Astley", "sasug", "NA")
print("Player Overview: " + str(overview))
