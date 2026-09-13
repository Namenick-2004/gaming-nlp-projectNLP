"""
Simple in-memory TTL cache for YouTube API responses and comment
lists, so repeated dashboard refreshes don't burn API quota or
re-run inference unnecessarily. Swap for Redis in production by
keeping the same get/set interface.
"""
from cachetools import TTLCache
from app.config import settings

_cache = TTLCache(maxsize=512, ttl=settings.CACHE_TTL_SECONDS)


def cache_get(key: str):
    return _cache.get(key)


def cache_set(key: str, value):
    _cache[key] = value
    return value
