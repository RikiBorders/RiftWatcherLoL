"""Tiny dotenv shim for tests.

This mirrors the small shim previously present at project root. Keeping it
inside `tests/` groups test-only helpers together.
"""

def load_dotenv(path=None):
    return None
