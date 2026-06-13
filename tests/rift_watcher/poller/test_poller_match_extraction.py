import json
import sys
import types
from datetime import datetime, timezone

# Provide a dummy dotenv module for tests to avoid external dependency
sys.modules.setdefault("dotenv", types.ModuleType("dotenv"))
setattr(sys.modules["dotenv"], "load_dotenv", lambda: None)

from rift_watcher.poller.poller import Poller


def load_match():
    with open("tests/testData/match.json", "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_extract_match_fields_full_timestamp():
    match = load_match()
    p = Poller(None, None, None)  # clients not needed for extraction
    fields = p._extract_match_fields(match)

    assert fields["riot_match_id"] == match["metadata"]["matchId"]
    assert fields["queue_type"] == match["info"]["gameMode"]
    assert fields["patch_version"] == match["info"]["gameVersion"]
    assert fields["game_duration_seconds"] == match["info"]["gameDuration"]

    # compute expected ISO from ms timestamp
    ts = match["info"]["gameStartTimestamp"]
    expected = datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc).isoformat()
    assert fields["started_at"] == expected


def test_extract_match_fields_missing_timestamp():
    match = load_match()
    # remove timestamp
    match_without_ts = dict(match)
    match_without_ts["info"] = dict(match_without_ts["info"])
    match_without_ts["info"].pop("gameStartTimestamp", None)

    p = Poller(None, None, None)
    fields = p._extract_match_fields(match_without_ts)

    assert fields["riot_match_id"] == match["metadata"]["matchId"]
    assert fields["started_at"] is None
