import types
from unittest.mock import MagicMock

import pytest

from rift_watcher.client import database_client


def make_response(data):
    return types.SimpleNamespace(data=data)


def make_table_mock(response_data=None):
    table = MagicMock()
    # chainable methods return the table mock
    table.select.return_value = table
    table.eq.return_value = table
    table.limit.return_value = table
    table.insert.return_value = table
    table.update.return_value = table
    table.upsert.return_value = table
    table.delete.return_value = table
    # set execute to return provided response data
    table.execute.return_value = make_response(response_data)
    return table


def test_get_player_by_puuid_not_found(monkeypatch):
    players_table = make_table_mock([])
    mock_client = MagicMock()
    mock_client.table.return_value = players_table

    monkeypatch.setattr(database_client, "create_client", lambda *args, **kwargs: mock_client)

    db = database_client.DatabaseClient(supabase_url="u", supabase_key="k")
    assert db.get_player_by_puuid("nonexistent") is None
    mock_client.table.assert_called_with(db.PLAYERS_TABLE)


def test_get_player_by_puuid_found(monkeypatch):
    payload = {"riot_puuid": "puuid", "summoner_name": "name"}
    players_table = make_table_mock([payload])
    mock_client = MagicMock()
    mock_client.table.return_value = players_table

    monkeypatch.setattr(database_client, "create_client", lambda *args, **kwargs: mock_client)
    db = database_client.DatabaseClient(supabase_url="u", supabase_key="k")
    result = db.get_player_by_puuid("puuid")
    assert result == payload


def test_create_player_and_update(monkeypatch):
    created = {"id": "1", "riot_puuid": "p", "summoner_name": "n"}
    players_table = make_table_mock([created])
    mock_client = MagicMock()
    mock_client.table.return_value = players_table

    monkeypatch.setattr(database_client, "create_client", lambda *args, **kwargs: mock_client)
    db = database_client.DatabaseClient(supabase_url="u", supabase_key="k")

    res = db.create_player("p", "n", "t", "EUW", current_rank=None)
    assert res == created

    # upsert
    upserted = {"id": "1", "riot_puuid": "p", "current_rank": "Gold"}
    players_table.execute.return_value = make_response([upserted])
    res2 = db.upsert_player(
        "p",
        "n",
        "t",
        "EUW",
        current_soloduo_rank="Gold",
        current_flex_rank=None,
    )
    assert res2 == upserted


def test_update_and_delete_player(monkeypatch):
    updated = {"id": "1", "riot_puuid": "p", "current_rank": "Platinum"}
    players_table = make_table_mock([updated])
    mock_client = MagicMock()
    mock_client.table.return_value = players_table

    monkeypatch.setattr(database_client, "create_client", lambda *args, **kwargs: mock_client)
    db = database_client.DatabaseClient(supabase_url="u", supabase_key="k")

    res = db.update_player_rank("p", "Platinum")
    assert res == updated

    updated_identity = {"id": "1", "riot_puuid": "p", "summoner_name": "new", "tagline": "t"}
    players_table.execute.return_value = make_response([updated_identity])
    res2 = db.update_player_identity("p", "new", "t")
    assert res2 == updated_identity

    # delete returns None; ensure delete chain invoked
    players_table.execute.return_value = make_response([])
    db.delete_player("p")
    players_table.delete.assert_called()


def test_player_match_performance_crud(monkeypatch):
    perf = {"puuid": "pid", "match_id": "mid", "kills": 5}
    table = make_table_mock([perf])
    mock_client = MagicMock()
    mock_client.table.return_value = table

    monkeypatch.setattr(database_client, "create_client", lambda *args, **kwargs: mock_client)
    db = database_client.DatabaseClient(supabase_url="u", supabase_key="k")

    # get
    got = db.get_player_match_performance("pid", "mid")
    assert got == perf

    # create
    table.execute.return_value = make_response([perf])
    created = db.create_player_match_performance(
        puuid="pid",
        match_id="mid",
        champion="champ",
        role="mid",
        kills=5,
        deaths=2,
        assists=7,
        kda_ratio=6.0,
        win=True,
        damage_share=0.2,
        cs_per_min=8.5,
    )
    assert created == perf

    # upsert
    table.execute.return_value = make_response([perf])
    up = db.upsert_player_match_performance(payload=perf)
    assert up == perf

    # bulk upsert empty
    assert db.bulk_upsert_player_match_performance([]) == []

    # bulk upsert non-empty
    table.execute.return_value = make_response([perf])
    res = db.bulk_upsert_player_match_performance([perf])
    assert res == [perf]

    # delete
    table.execute.return_value = make_response([])
    db.delete_player_match_performance("pid", "mid")
    table.delete.assert_called()


def test_matches_crud(monkeypatch):
    m = {"id": "mid", "riot_match_id": "rmid"}
    table = make_table_mock([m])
    mock_client = MagicMock()
    mock_client.table.return_value = table

    monkeypatch.setattr(database_client, "create_client", lambda *args, **kwargs: mock_client)
    db = database_client.DatabaseClient(supabase_url="u", supabase_key="k")

    assert db.get_match_by_id("mid") == m
    assert db.get_match_by_riot_match_id("rmid") == m

    table.execute.return_value = make_response([m])
    created = db.create_match("rmid", "SR", "13.10", 1800, "2026-05-31T12:00:00Z")
    assert created == m

    table.execute.return_value = make_response([m])
    up = db.upsert_match(payload=m)
    assert up == m


def test_get_player_by_id_and_client_property(monkeypatch):
    # verify get_player_by_id behavior
    payload = {"id": "player-1", "riot_puuid": "puuid"}
    players_table = make_table_mock([payload])
    mock_client = MagicMock()
    mock_client.table.return_value = players_table

    monkeypatch.setattr(database_client, "create_client", lambda *args, **kwargs: mock_client)
    db = database_client.DatabaseClient(supabase_url="u", supabase_key="k")

    # client property should expose the raw client
    assert db.client is mock_client

    # get by id
    res = db.get_player_by_id("player-1")
    assert res == payload
