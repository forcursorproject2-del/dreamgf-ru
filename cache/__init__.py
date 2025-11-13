import asyncio
import time
from typing import Dict, Any, Optional
from config.settings import REDIS_URL
import logging

logger = logging.getLogger(__name__)

class MemoryCache:
    """In-memory cache with TTL support"""

    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[bytes]:
        """Get value from cache"""
        async with self._lock:
            if key in self._data:
                entry = self._data[key]
                if time.time() < entry['expire']:
                    return entry['value']
                else:
                    del self._data[key]
            return None

    async def set(self, key: str, value: bytes, expire: int = 3600):
        """Set value in cache with TTL"""
        async with self._lock:
            self._data[key] = {
                'value': value,
                'expire': time.time() + expire
            }

    async def delete(self, key: str):
        """Delete key from cache"""
        async with self._lock:
            self._data.pop(key, None)

    async def incr(self, key: str) -> int:
        """Increment counter"""
        async with self._lock:
            current = await self.get_user_rate_limit(key.split(':')[-1]) if 'rate_limit' in key else 0
            new_value = current + 1
            await self.set(key, str(new_value).encode(), expire=60)
            return new_value

    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get list range"""
        async with self._lock:
            data = await self.get(key)
            if data:
                try:
                    messages = data.decode()
                    if messages.startswith('['):
                        import json
                        lst = json.loads(messages)
                        return lst[start:end+1] if isinstance(lst, list) else []
                except:
                    pass
            return []

    async def lpush(self, key: str, value):
        """Push to list"""
        async with self._lock:
            current = await self.lrange(key, 0, -1)
            current.insert(0, value)
            import json
            await self.set(key, json.dumps(current).encode(), expire=30*24*60*60)

    async def ltrim(self, key: str, start: int, end: int):
        """Trim list"""
        async with self._lock:
            current = await self.lrange(key, 0, -1)
            if current:
                trimmed = current[start:end+1]
                import json
                await self.set(key, json.dumps(trimmed).encode(), expire=30*24*60*60)

    async def expire(self, key: str, seconds: int):
        """Set expiration"""
        async with self._lock:
            if key in self._data:
                entry = self._data[key]
                entry['expire'] = time.time() + seconds

    async def close(self):
        """Close cache"""
        async with self._lock:
            self._data.clear()

    # Additional methods for compatibility
    async def get_chat_history(self, user_id: int, limit: int) -> list:
        """Get chat history for user"""
        key = f"user:{user_id}:messages"
        messages = await self.lrange(key, 0, limit - 1)
        return messages

    async def add_to_chat_history(self, user_id: int, message: str, response: str):
        """Add message to chat history"""
        key = f"user:{user_id}:messages"
        import json
        data = json.dumps({"user": message, "assistant": response})
        await self.lpush(key, data)
        await self.ltrim(key, 0, 50)  # Keep last 50 messages

    async def get_image_cache(self, user_id: int, prompt_hash: str) -> bytes:
        """Get cached image"""
        key = f"user:{user_id}:image:{prompt_hash}"
        return await self.get(key)

    async def set_image_cache(self, user_id: int, prompt_hash: str, image_data: bytes):
        """Cache image data"""
        key = f"user:{user_id}:image:{prompt_hash}"
        await self.set(key, image_data, expire=24*60*60)

    async def get_user_rate_limit(self, user_id: int) -> int:
        """Get rate limit count"""
        key = f"user:{user_id}:rate_limit"
        data = await self.get(key)
        return int(data.decode()) if data else 0

    async def increment_rate_limit(self, user_id: int):
        """Increment rate limit"""
        key = f"user:{user_id}:rate_limit"
        current = await self.get_user_rate_limit(user_id)
        await self.set(key, str(current + 1).encode(), expire=60)

    async def get_user_photo_count(self, user_id: int) -> int:
        """Get photo count"""
        key = f"user:{user_id}:photo_count"
        data = await self.get(key)
        return int(data.decode()) if data else 0

    async def increment_photo_count(self, user_id: int):
        """Increment photo count"""
        key = f"user:{user_id}:photo_count"
        current = await self.get_user_photo_count(user_id)
        await self.set(key, str(current + 1).encode(), expire=24*60*60)

# Initialize cache
if REDIS_URL == "memory://" or not REDIS_URL:
    cache = MemoryCache()
else:
    try:
        import redis.asyncio as redis
        cache = redis.from_url(REDIS_URL)
    except ImportError:
        logger.warning("Redis not available, using memory cache")
        cache = MemoryCache()
