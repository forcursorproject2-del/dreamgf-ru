import json
import hashlib
import asyncio
import time
from typing import Dict, Any, Optional
from config.settings import REDIS_URL, CHAT_HISTORY_LIMIT
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

    async def cleanup_expired(self):
        """Remove expired entries"""
        async with self._lock:
            current_time = time.time()
            expired_keys = [k for k, v in self._data.items() if current_time >= v['expire']]
            for key in expired_keys:
                del self._data[key]

class Cache:
    def __init__(self, redis_url: str = REDIS_URL):
        if redis_url == "memory://" or not redis_url:
            self._backend = MemoryCache()
            self._is_memory = True
        else:
            try:
                import redis.asyncio as redis
                self._backend = redis.from_url(redis_url)
                self._is_memory = False
            except ImportError:
                logger.warning("Redis not available, using memory cache")
                self._backend = MemoryCache()
                self._is_memory = True

    async def get_chat_history(self, user_id: int) -> list:
        """Get chat history for user"""
        try:
            if self._is_memory:
                key = f"user:{user_id}:messages"
                data = await self._backend.get(key)
                if data:
                    messages = json.loads(data.decode())
                    return messages[-CHAT_HISTORY_LIMIT:]
                return []
            else:
                messages = await self._backend.lrange(key, 0, CHAT_HISTORY_LIMIT - 1)
                return [json.loads(msg) for msg in messages]
        except Exception as e:
            logger.error(f"Failed to get chat history for {user_id}: {e}")
            return []

    async def add_message(self, user_id: int, message: str, response: str):
        """Add message pair to chat history"""
        try:
            if self._is_memory:
                key = f"user:{user_id}:messages"
                current = await self.get_chat_history(user_id)
                current.append({"user": message, "assistant": response})
                data = json.dumps(current[-CHAT_HISTORY_LIMIT:]).encode()
                await self._backend.set(key, data, expire=30 * 24 * 60 * 60)
            else:
                key = f"user:{user_id}:messages"
                data = json.dumps({"user": message, "assistant": response})
                await self._backend.lpush(key, data)
                await self._backend.ltrim(key, 0, CHAT_HISTORY_LIMIT - 1)
                await self._backend.expire(key, 30 * 24 * 60 * 60)
        except Exception as e:
            logger.error(f"Failed to add message for {user_id}: {e}")

    async def add_to_chat_history(self, user_id: int, message: str, response: str):
        """Alias for add_message"""
        await self.add_message(user_id, message, response)

    async def get_image_cache(self, user_id: int, prompt_hash: str) -> bytes:
        """Get cached image"""
        try:
            key = f"user:{user_id}:image:{prompt_hash}"
            if self._is_memory:
                return await self._backend.get(key)
            else:
                return await self._backend.get(key)
        except Exception as e:
            logger.error(f"Failed to get cached image for {user_id}: {e}")
            return None

    async def set_image_cache(self, user_id: int, prompt_hash: str, image_data: bytes):
        """Cache image data"""
        try:
            key = f"user:{user_id}:image:{prompt_hash}"
            if self._is_memory:
                await self._backend.set(key, image_data, expire=24 * 60 * 60)
            else:
                await self._backend.set(key, image_data, ex=24 * 60 * 60)
        except Exception as e:
            logger.error(f"Failed to cache image for {user_id}: {e}")

    async def get_user_rate_limit(self, user_id: int) -> int:
        """Get current message count for rate limiting"""
        try:
            key = f"user:{user_id}:rate_limit"
            if self._is_memory:
                data = await self._backend.get(key)
                return int(data.decode()) if data else 0
            else:
                count = await self._backend.get(key)
                return int(count) if count else 0
        except Exception as e:
            logger.error(f"Failed to get rate limit for {user_id}: {e}")
            return 0

    async def increment_rate_limit(self, user_id: int):
        """Increment message count for rate limiting"""
        try:
            key = f"user:{user_id}:rate_limit"
            if self._is_memory:
                current = await self.get_user_rate_limit(user_id)
                await self._backend.set(key, str(current + 1).encode(), expire=60)
            else:
                await self._backend.incr(key)
                await self._backend.expire(key, 60)
        except Exception as e:
            logger.error(f"Failed to increment rate limit for {user_id}: {e}")

    async def get_user_photo_count(self, user_id: int) -> int:
        """Get current photo count for user"""
        try:
            key = f"user:{user_id}:photo_count"
            if self._is_memory:
                data = await self._backend.get(key)
                return int(data.decode()) if data else 0
            else:
                count = await self._backend.get(key)
                return int(count) if count else 0
        except Exception as e:
            logger.error(f"Failed to get photo count for {user_id}: {e}")
            return 0

    async def increment_photo_count(self, user_id: int):
        """Increment photo count for user"""
        try:
            key = f"user:{user_id}:photo_count"
            if self._is_memory:
                current = await self.get_user_photo_count(user_id)
                await self._backend.set(key, str(current + 1).encode(), expire=24 * 60 * 60)
            else:
                await self._backend.incr(key)
                await self._backend.expire(key, 24 * 60 * 60)
        except Exception as e:
            logger.error(f"Failed to increment photo count for {user_id}: {e}")

    async def close(self):
        """Close connection if Redis"""
        if not self._is_memory:
            await self._backend.close()

def get_prompt_hash(prompt: str, character: str) -> str:
    """Generate hash for prompt + character"""
    return hashlib.md5(f"{prompt}:{character}".encode()).hexdigest()
