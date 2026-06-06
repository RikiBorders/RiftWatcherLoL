from unittest.mock import MagicMock

from rift_watcher.adapter.riot_adapter import RiotAdapter


def test_translate_player_profile_maps_solo_and_flex_ranks():
    riot_client = MagicMock()
    riot_client.region = "NA"
    adapter = RiotAdapter(database_client=MagicMock(), riot_client=riot_client)

    raw_profile_data = {
        "player_id": "player-123",
        "display_name": "Rik Astley#sasug",
        "region": "NA",
        "solo_queue": {
            "queueType": "RANKED_SOLO_5x5",
            "tier": "EMERALD",
            "rank": "II",
            "puuid": "rrIL8qCiL8DqrzvKW0opmmX0p0i-0ebdVrARDEFDGd1aZGNvIZSEE0RTzWBcJQdJdy5RXdtnZB4gYA",
            "leaguePoints": 96,
            "wins": 126,
            "losses": 100,
            "veteran": False,
            "inactive": False,
            "freshBlood": False,
            "hotStreak": True,
        },
        "flex_queue": {
            "queueType": "RANKED_FLEX_SR",
            "tier": "GOLD",
            "rank": "III",
            "puuid": "rrIL8qCiL8DqrzvKW0opmmX0p0i-0ebdVrARDEFDGd1aZGNvIZSEE0RTzWBcJQdJdy5RXdtnZB4gYA",
            "leaguePoints": 33,
            "wins": 7,
            "losses": 7,
            "veteran": False,
            "inactive": False,
            "freshBlood": False,
            "hotStreak": False,
        },
    }

    profile = adapter.translate_player_profile(raw_profile_data)

    assert profile["player_id"] == "player-123"
    assert profile["display_name"] == "Rik Astley#sasug"
    assert profile["region"] == "NA"
    assert profile["rank"] == "Emerald II"
    assert profile["ranked_tier"] == "EMERALD"
    assert profile["ranked_division"] == "II"
    assert profile["flex_rank"] == "Gold III"
    assert profile["flex_ranked_tier"] == "GOLD"
    assert profile["flex_ranked_division"] == "III"


def test_translate_player_profile_defaults_unranked_when_no_queues():
    riot_client = MagicMock()
    riot_client.region = "NA"
    adapter = RiotAdapter(database_client=MagicMock(), riot_client=riot_client)

    raw_profile_data = {
        "display_name": "Rik Astley#sasug",
        "region": "NA",
    }

    profile = adapter.translate_player_profile(raw_profile_data)

    assert profile["rank"] == "Unranked"
    assert profile["ranked_tier"] is None
    assert profile["ranked_division"] is None
    assert profile["flex_rank"] == "Unranked"
    assert profile["flex_ranked_tier"] is None
    assert profile["flex_ranked_division"] is None
