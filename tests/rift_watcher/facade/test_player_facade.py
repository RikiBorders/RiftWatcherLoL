from unittest.mock import MagicMock

import pytest

from rift_watcher.facade.player_facade import PlayerFacade


def test_get_player_overview_delegates_to_riot_adapter():
    riot_adapter = MagicMock()
    expected = {"puuid": "p-1", "display_name": "Test#1"}
    riot_adapter.fetch_player_profile.return_value = expected

    stat_calculator = MagicMock()
    facade = PlayerFacade(riot_adapter=riot_adapter, stat_calculator=stat_calculator)

    res = facade.get_player_overview("Name", "Tag", "EUW")

    assert res is expected
    riot_adapter.fetch_player_profile.assert_called_once_with("Name", "Tag", "EUW")
    # stat_calculator is provided but not used by the current API surface
    stat_calculator.assert_not_called()


def test_get_player_match_data_delegates_to_riot_adapter():
    riot_adapter = MagicMock()
    expected_matches = [{"match_id": "m1"}, {"match_id": "m2"}]
    riot_adapter.fetch_player_match_data.return_value = expected_matches

    stat_calculator = MagicMock()
    facade = PlayerFacade(riot_adapter=riot_adapter, stat_calculator=stat_calculator)

    res = facade.get_player_match_data("puuid-1", "NA")

    assert res == expected_matches
    riot_adapter.fetch_player_match_data.assert_called_once_with("puuid-1", "NA")


def test_facade_exposes_stat_calculator_and_propagates_exceptions():
    riot_adapter = MagicMock()
    riot_adapter.fetch_player_profile.side_effect = RuntimeError("boom")
    stat_calculator = MagicMock()
    facade = PlayerFacade(riot_adapter=riot_adapter, stat_calculator=stat_calculator)

    assert facade.stat_calculator is stat_calculator

    with pytest.raises(RuntimeError):
        facade.get_player_overview("x", "y", "z")
