import logging
from typing import Any, Dict

from ..facade.player_facade import PlayerFacade
from ..type.types import PlayerOverview

logger = logging.getLogger(__name__)


class RiftWatcherAPI:
    """
    Thin service layer over PlayerFacade.

    Responsibilities:
    - Call domain logic (PlayerFacade)
    - Normalize output for HTTP (dict)
    - Centralize logging + error context
    """

    def __init__(self, player_facade: PlayerFacade):
        self.player_facade = player_facade

    def get_player_overview(
        self,
        game_name: str,
        tag_line: str,
        region: str
    ) -> Dict[str, Any]:
        """
        Retrieve player overview data for API consumption.
        """
        logger.info(
            "Fetching player overview: %s#%s (%s)",
            game_name,
            tag_line,
            region
        )
        try:
            overview: PlayerOverview = self.player_facade.get_player_overview(
                game_name,
                tag_line,
                region
            )
            # Normalize to dict for Flask/JSON serialization
            return self._to_dict(overview)

        except Exception as e:
            logger.exception(
                "Failed to fetch player overview for %s#%s (%s)",
                game_name,
                tag_line,
                region
            )
            raise RuntimeError("Failed to fetch player overview") from e

    def _to_dict(self, overview: PlayerOverview) -> Dict[str, Any]:
        """
        Converts domain object → JSON-safe dict.

        Keeps Flask layer dumb and predictable.
        """
        if hasattr(overview, "__dict__"):
            return overview.__dict__

        # fallback for dataclasses or pydantic-like objects
        if hasattr(overview, "model_dump"):  # pydantic v2
            return overview.model_dump()

        if hasattr(overview, "dict"):  # pydantic v1
            return overview.dict()

        return dict(overview)