"""Simple in-memory cache service."""
from typing import Any, Optional, Dict
import time
import logging
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class CacheService:
    """Simple cache service with TTL support."""

    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        """Initialize cache."""
        self.cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.hits = 0
        self.misses = 0

        logger.info(f"Cache initialized with maxsize={maxsize}, ttl={ttl}s")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = self.cache.get(key)

        if value is not None:
            self.hits += 1
            logger.debug(f"Cache hit for key: {key[:50]}")
        else:
            self.misses += 1
            logger.debug(f"Cache miss for key: {key[:50]}")

        return value

    def set(self, key: str, value: Any):
        """Set value in cache."""
        self.cache[key] = value
        logger.debug(f"Cached value for key: {key[:50]}")

    def delete(self, key: str):
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Deleted cache key: {key[:50]}")

    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "maxsize": self.cache.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
        }
