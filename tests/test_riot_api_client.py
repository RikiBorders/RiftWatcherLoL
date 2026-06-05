"""Tests for the Riot API client."""

import requests

from rift_watcher.client.riot_api_client import RiotAPIClient


def test_fetch_player_profile_returns_expected_profile(monkeypatch):
    riot_client = RiotAPIClient(region="EUW")

    def fake_get(url, headers, timeout):
        class FakeResponse:
            def __init__(self, json_data, status_code):
                self._json = json_data
                self.status_code = status_code

            def json(self):
                return self._json

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.HTTPError(f"{self.status_code} error")

        if "/lol/summoner/v4/summoners/by-name/" in url:
            return FakeResponse({"id": "12345", "name": "TestSummoner"}, 200)

        if "/lol/league/v4/entries/by-summoner/12345" in url:
            return FakeResponse([
                {
                    "queueType": "RANKED_SOLO_5x5",
                    "tier": "GOLD",
                    "rank": "III",
                }
            ], 200)

        raise AssertionError(f"Unexpected URL called: {url}")

    monkeypatch.setattr("rift_watcher.client.riot_api_client.requests.get", fake_get)

    profile = riot_client.fetch_player_profile(summoner_name="TestSummoner", region="EUW")

    assert isinstance(profile, dict)
    assert profile["player_id"] == "12345"
    assert profile["display_name"] == "TestSummoner"
    assert profile["region"] == "EUW"
    assert profile["rank"] == "GOLD III"
    assert profile["ranked_tier"] == "GOLD"
    assert profile["ranked_division"] == "III"


def test_fetch_player_profile_reflects_region_and_summoner_name(monkeypatch):
    riot_client = RiotAPIClient(region="KR")

    def fake_get(url, headers, timeout):
        class FakeResponse:
            def __init__(self, json_data, status_code):
                self._json = json_data
                self.status_code = status_code

            def json(self):
                return self._json

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.HTTPError(f"{self.status_code} error")

        if "/lol/summoner/v4/summoners/by-name/" in url:
            return FakeResponse({"id": "abcdef", "name": "AnotherPlayer"}, 200)

        if "/lol/league/v4/entries/by-summoner/abcdef" in url:
            return FakeResponse([], 200)

        raise AssertionError(f"Unexpected URL called: {url}")

    monkeypatch.setattr("rift_watcher.client.riot_api_client.requests.get", fake_get)

    profile = riot_client.fetch_player_profile(summoner_name="AnotherPlayer", region="KR")

    assert profile["player_id"] == "abcdef"
    assert profile["display_name"] == "AnotherPlayer"
    assert profile["region"] == "KR"
    assert profile["rank"] == "Unranked"
    assert profile["ranked_tier"] is None
    assert profile["ranked_division"] is None
