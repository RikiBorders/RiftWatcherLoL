
class LruCache(self):
    """Simple LRU cache implementation for in-memory caching."""

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache: dict[str, any] = {}
        self.access_order: list[str] = []

    def get(self, key: str) -> any | None:
        """Retrieve a value from the cache by key."""
        if key in self.cache:
            # Update access order
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def put(self, key: str, value: any) -> None:
        """Add or update a value in the cache."""
        if key in self.cache:
            # Update existing key
            self.access_order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Evict least recently used item
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]
        # Add new key-value pair
        self.cache[key] = value
        self.access_order.append(key)

    def clear(self) -> None:
        """Clear the entire cache."""
        self.cache.clear()
        self.access_order.clear()