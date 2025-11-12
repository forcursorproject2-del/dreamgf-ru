import asyncio
import time
import redis.asyncio as redis
from config.settings import REDIS_URL
import logging

logger = logging.getLogger(__name__)

class MemoryCache:
    """In-memory cache fallback"""

    def __init__(self):
        self._cache = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> bytes:
        async with self._lock:
            if key in self._cache:
                value, expire_time = self._cache[key]
                if expire_time is None or time.time() < expire_time:
                    return value
                else:
                    del self._cache[key]
            return None

    async def set(self, key: str, value: bytes, ex: int = None):
        async with self._lock:
            expire_time = time.time() + ex if ex else None
            self._cache[key] = (value, expire_time)

    async def incr(self, key: str) -> int:
        async with self._lock:
            if key in self._cache:
                value, expire_time = self._cache[key]
                if isinstance(value, int):
                    new_value = value + 1
                else:
                    new_value = 1
            else:
                new_value = 1
            expire_time = time.time() + 60  # Default 1 minute
            self._cache[key] = (new_value, expire_time)
            return new_value

    async def lrange(self, key: str, start: int, end: int) -> list:
        async with self._lock:
            if key in self._cache:
                value, expire_time = self._cache[key]
                if isinstance(value, list):
                    return value[start:end+1]
            return []

    async def lpush(self, key: str, value):
        async with self._lock:
            if key in self._cache:
                cache_value, expire_time = self._cache[key]
                if isinstance(cache_value, list):
                    cache_value.insert(0, value)
                else:
                    self._cache[key] = ([value], expire_time)
            else:
                self._cache[key] = ([value], None)

    async def ltrim(self, key: str, start: int, end: int):
        async with self._lock:
            if key in self._cache:
                value, expire_time = self._cache[key]
                if isinstance(value, list):
                    self._cache[key] = (value[start:end+1], expire_time)

    async def expire(self, key: str, seconds: int):
        async with self._lock:
            if key in self._cache:
                value, _ = self._cache[key]
                expire_time = time.time() + seconds
                self._cache[key] = (value, expire_time)

    async def close(self):
        async with self._lock:
            self._cache.clear()

# Initialize cache
if REDIS_URL.startswith("memory://"):
    cache = MemoryCache()
else:
    cache = redis.from_url(REDIS_URL)
