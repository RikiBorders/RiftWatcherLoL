"""Lightweight shim for the `supabase` package used in tests.

This module exists only to satisfy imports during unit tests. The
actual DatabaseClient tests monkeypatch `create_client` as needed, so
this shim does not attempt to implement the full Supabase client.
"""


class Client:  # pragma: no cover - shim for tests
    pass


def create_client(url: str, key: str) -> Client:  # pragma: no cover - shim
    raise RuntimeError("create_client should be monkeypatched in tests or replaced with real supabase client")
