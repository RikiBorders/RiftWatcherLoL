"""CLI invoker for Rift Watcher API and adapter operations.

This module exposes a small command line interface for quick local
verification of the core services without running the full Flask app.
"""

import argparse
import json
import logging
import os
from typing import Any

from dotenv import load_dotenv

from rift_watcher.api.rift_watcher_api import RiftWatcherAPI
from rift_watcher.adapter.riot_adapter import RiotAdapter
from rift_watcher.client.database_client import DatabaseClient
from rift_watcher.client.riot_api_client import RiotAPIClient
from rift_watcher.facade.player_facade import PlayerFacade
from rift_watcher.utils.stat_calculator import StatCalculator

logger = logging.getLogger(__name__)


class Invoker:
    """Simple API invoker for Rift Watcher endpoints."""

    def __init__(self, api: RiftWatcherAPI, adapter: RiotAdapter) -> None:
        self.api = api
        self.adapter = adapter

    def player_overview(self, game_name: str, tag_line: str, region: str) -> Any:
        """Call the player overview endpoint."""
        return self.api.get_player_overview(game_name, tag_line, region)

    def update_matches(self) -> Any:
        """Refresh the match tables using Riot API data."""
        return self.adapter.update_matches_table()

    def recent_matches(self, puuid: str, count: int, region: str) -> Any:
        """Fetch recent matches for a player."""
        return self.adapter.get_recent_match_data(puuid, count, region)

    def player_match_performances(self, puuid: str) -> Any:
        """Query player match performance records by PUUID."""
        return self.adapter.get_player_match_performances_by_puuid(puuid)


def build_invoker(
    region: str | None = None,
    supabase_url: str | None = None,
    supabase_key: str | None = None,
) -> Invoker:
    """Build the invoker with a configured Riot and Supabase client."""
    load_dotenv()

    effective_region = region or os.getenv("RIOT_REGION", "NA")
    db_client = DatabaseClient(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
    )
    riot_client = RiotAPIClient(region=effective_region)
    riot_adapter = RiotAdapter(database_client=db_client, riot_client=riot_client)
    stat_calculator = StatCalculator(database_client=db_client, riot_adapter=riot_adapter)
    player_facade = PlayerFacade(riot_adapter=riot_adapter, stat_calculator=stat_calculator)
    api = RiftWatcherAPI(player_facade=player_facade)

    return Invoker(api=api, adapter=riot_adapter)


def print_json(value: Any) -> None:
    """Serialize the result as JSON for CLI output."""
    print(json.dumps(value, indent=2, default=str))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Invoke Rift Watcher operations from the command line."
    )
    parser.add_argument(
        "--region",
        default=os.getenv("RIOT_REGION", "NA"),
        help="Riot region code, e.g. NA, EUW.",
    )
    parser.add_argument(
        "--supabase-url",
        default=os.getenv("SUPABASE_URL"),
        help="Supabase project URL.",
    )
    parser.add_argument(
        "--supabase-key",
        default=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        help="Supabase service role key.",
    )

    subparsers = parser.add_subparsers(dest="command")

    player_overview = subparsers.add_parser(
        "player-overview",
        help="Fetch a player overview through the API layer.",
    )
    player_overview.add_argument("--game-name", required=True, help="Summoner name.")
    player_overview.add_argument("--tag-line", required=True, help="Riot tag line.")

    update_matches = subparsers.add_parser(
        "update-matches",
        help="Fetch recent match IDs and update the database.",
    )

    recent_matches = subparsers.add_parser(
        "recent-matches",
        help="Fetch recent match payloads for a player.",
    )
    recent_matches.add_argument("--puuid", required=True, help="Player PUUID.")
    recent_matches.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of recent matches to retrieve.",
    )

    performances = subparsers.add_parser(
        "player-performances",
        help="Query stored player match performance records by PUUID.",
    )
    performances.add_argument("--puuid", required=True, help="Player PUUID.")

    return parser.parse_args(argv)


def ask_non_empty(prompt: str, default: str | None = None) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        if default is not None:
            return default
        print("This value is required. Please try again.")


def select_command() -> str | None:
    commands = [
        "player-overview",
        "update-matches",
        "recent-matches",
        "player-performances",
        "quit",
    ]

    print("\nRift Watcher CLI")
    print("Choose a command to run:")
    for index, command in enumerate(commands, start=1):
        print(f"  {index}. {command}")

    while True:
        choice = input("Select a command number or name: ").strip().lower()
        if not choice:
            print("Please enter a command.")
            continue

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(commands):
                return commands[index]
            print("Invalid selection number.")
            continue

        if choice in commands:
            return choice

        print("Unknown command. Please enter a valid name or number.")


def interactive_mode(region: str, supabase_url: str | None, supabase_key: str | None) -> int:
    command = select_command()
    if not command or command == "quit":
        print("Exiting CLI.")
        return 0

    invoker = build_invoker(
        region=region,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
    )

    if command == "player-overview":
        game_name = ask_non_empty("Summoner name: ")
        tag_line = ask_non_empty("Tag line: ")
        region = ask_non_empty(f"Region [{region}]: ", default=region)
        print_json(invoker.player_overview(game_name=game_name, tag_line=tag_line, region=region))
        return 0

    if command == "update-matches":
        response = invoker.update_matches()
        if response is None:
            print("Update completed.")
        else:
            print_json(response)
        return 0

    if command == "recent-matches":
        puuid = ask_non_empty("Player PUUID: ")
        count_input = input("Number of recent matches [5]: ").strip()
        count = int(count_input) if count_input.isdigit() else 5
        print_json(invoker.recent_matches(puuid=puuid, count=count, region=region))
        return 0

    if command == "player-performances":
        puuid = ask_non_empty("Player PUUID: ")
        print_json(invoker.player_match_performances(puuid))
        return 0

    logger.error("Interactive command resolution failed for %s", command)
    return 1


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.command is None:
        return interactive_mode(
            region=args.region,
            supabase_url=args.supabase_url,
            supabase_key=args.supabase_key,
        )

    invoker = build_invoker(
        region=args.region,
        supabase_url=args.supabase_url,
        supabase_key=args.supabase_key,
    )

    if args.command == "player-overview":
        response = invoker.player_overview(
            game_name=args.game_name,
            tag_line=args.tag_line,
            region=args.region,
        )
        print_json(response)
        return 0

    if args.command == "update-matches":
        response = invoker.update_matches()
        if response is None:
            print("Update completed.")
        else:
            print_json(response)
        return 0

    if args.command == "recent-matches":
        response = invoker.recent_matches(
            puuid=args.puuid,
            count=args.count,
            region=args.region,
        )
        print_json(response)
        return 0

    if args.command == "player-performances":
        response = invoker.player_match_performances(args.puuid)
        print_json(response)
        return 0

    logger.error("Unknown command: %s", args.command)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
