"""Tests for the Riot API client."""

from rift_watcher.client.riot_api_client import RiotAPIClient


def test_fetch_player_profile_returns_expected_profile():
    riot_client = RiotAPIClient(api_key="test-key", region="EUW")
    profile = riot_client.fetch_player_profile(player_id="12345")

    assert isinstance(profile, dict)
    assert profile["player_id"] == "12345"
    assert profile["display_name"] == "Player_12345"
    assert profile["region"] == "EUW"
    assert profile["rank"] == "Unranked"
    assert profile["ranked_tier"] is None
    assert profile["ranked_division"] is None


def test_fetch_player_profile_reflects_region_and_player_id():
    riot_client = RiotAPIClient(api_key="test-key", region="KR")
    profile = riot_client.fetch_player_profile(player_id="abcdef")

    assert profile["player_id"] == "abcdef"
    assert profile["display_name"] == "Player_abcdef"
    assert profile["region"] == "KR"
