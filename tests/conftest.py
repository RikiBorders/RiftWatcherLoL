import pytest


@pytest.fixture(autouse=True)
def set_supabase_env(monkeypatch):
    """Ensure SUPABASE env vars are present so `supabase.create_client`
    in the real package does not fail during test collection.
    """
    monkeypatch.setenv("SUPABASE_URL", "http://example.local")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "fake-key")
