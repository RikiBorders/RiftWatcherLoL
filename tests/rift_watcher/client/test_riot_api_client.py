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

        if "/riot/account/v1/accounts/by-riot-id/" in url:
            return FakeResponse({
                "puuid": "puuid-123",
                "gameName": "TestSummoner",
                "tagLine": "EUW1",
            }, 200)

        if "/lol/summoner/v4/summoners/by-puuid/puuid-123" in url:
            return FakeResponse({
                "id": "12345",
                "profileIconId": 123,
                "summonerLevel": 50,
                "puuid": "puuid-123",
            }, 200)

        if "/lol/league/v4/entries/by-puuid/puuid-123" in url:
            return FakeResponse([
                {
                    "queueType": "RANKED_SOLO_5x5",
                    "tier": "GOLD",
                    "rank": "III",
                }
            ], 200)

        raise AssertionError(f"Unexpected URL called: {url}")

    monkeypatch.setattr("rift_watcher.client.riot_api_client.requests.get", fake_get)

    profile = riot_client.fetch_player_profile(
        game_name="TestSummoner",
        tag_line="EUW1",
        region="EUW",
    )

    assert isinstance(profile, dict)
    assert profile["display_name"] == "TestSummoner#EUW1"
    assert profile["profile_icon_id"] == 123
    assert profile["summoner_level"] == 50
    assert profile["puuid"] == "puuid-123"
    assert profile["solo_queue"]["tier"] == "GOLD"
    assert profile["solo_queue"]["rank"] == "III"
    assert profile["flex_queue"] is None


def test_fetch_player_profile_reflects_region_and_game_name_tag_line(monkeypatch):
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

        if "/riot/account/v1/accounts/by-riot-id/" in url:
            return FakeResponse({
                "puuid": "puuid-456",
                "gameName": "AnotherPlayer",
                "tagLine": "KR1",
            }, 200)

        if "/lol/summoner/v4/summoners/by-puuid/puuid-456" in url:
            return FakeResponse({
                "id": "abcdef",
                "profileIconId": 321,
                "summonerLevel": 20,
                "puuid": "puuid-456",
            }, 200)

        if "/lol/league/v4/entries/by-puuid/puuid-456" in url:
            return FakeResponse([], 200)

        raise AssertionError(f"Unexpected URL called: {url}")

    monkeypatch.setattr("rift_watcher.client.riot_api_client.requests.get", fake_get)

    profile = riot_client.fetch_player_profile(
        game_name="AnotherPlayer",
        tag_line="KR1",
        region="KR",
    )

    assert profile["display_name"] == "AnotherPlayer#KR1"
    assert profile["profile_icon_id"] == 321
    assert profile["summoner_level"] == 20
    assert profile["puuid"] == "puuid-456"
    assert profile["solo_queue"] is None
    assert profile["flex_queue"] is None
