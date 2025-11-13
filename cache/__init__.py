import redis.asyncio as redis
import json
import hashlib
from config.settings import REDIS_URL, CHAT_HISTORY_LIMIT
import logging

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self, redis_url: str = REDIS_URL):
        self.redis = redis.from_url(redis_url)

    async def get_chat_history(self, user_id: int) -> list:
        """Get chat history for user"""
        try:
            key = f"user:{user_id}:messages"
            messages = await self.redis.lrange(key, 0, CHAT_HISTORY_LIMIT - 1)
            return [json.loads(msg) for msg in messages]
        except Exception as e:
            logger.error(f"Failed to get chat history for {user_id}: {e}")
            return []

    async def add_message(self, user_id: int, message: str, response: str):
        """Add message pair to chat history"""
        try:
            key = f"user:{user_id}:messages"
            data = json.dumps({"user": message, "assistant": response})
            await self.redis.lpush(key, data)
            await self.redis.ltrim(key, 0, CHAT_HISTORY_LIMIT - 1)
            # Set expiration to 30 days
            await self.redis.expire(key, 30 * 24 * 60 * 60)
        except Exception as e:
            logger.error(f"Failed to add message for {user_id}: {e}")

    async def add_to_chat_history(self, user_id: int, message: str, response: str):
        """Alias for add_message"""
        await self.add_message(user_id, message, response)

    async def get_image_cache(self, user_id: int, prompt_hash: str) -> bytes:
        """Get cached image"""
        try:
            key = f"user:{user_id}:image:{prompt_hash}"
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Failed to get cached image for {user_id}: {e}")
            return None

    async def set_image_cache(self, user_id: int, prompt_hash: str, image_data: bytes):
        """Cache image data"""
        try:
            key = f"user:{user_id}:image:{prompt_hash}"
            await self.redis.set(key, image_data, ex=24 * 60 * 60)  # 24 hours
        except Exception as e:
            logger.error(f"Failed to cache image for {user_id}: {e}")

    async def get_user_rate_limit(self, user_id: int) -> int:
        """Get current message count for rate limiting"""
        try:
            key = f"user:{user_id}:rate_limit"
            count = await self.redis.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Failed to get rate limit for {user_id}: {e}")
            return 0

    async def increment_rate_limit(self, user_id: int):
        """Increment message count for rate limiting"""
        try:
            key = f"user:{user_id}:rate_limit"
            await self.redis.incr(key)
            await self.redis.expire(key, 60)  # Reset every minute
        except Exception as e:
            logger.error(f"Failed to increment rate limit for {user_id}: {e}")

    async def get_user_photo_count(self, user_id: int) -> int:
        """Get current photo count for user"""
        try:
            key = f"user:{user_id}:photo_count"
            count = await self.redis.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Failed to get photo count for {user_id}: {e}")
            return 0

    async def increment_photo_count(self, user_id: int):
        """Increment photo count for user"""
        try:
            key = f"user:{user_id}:photo_count"
            await self.redis.incr(key)
            await self.redis.expire(key, 24 * 60 * 60)  # Reset every day
        except Exception as e:
            logger.error(f"Failed to increment photo count for {user_id}: {e}")

    async def close(self):
        """Close Redis connection"""
        await self.redis.close()

def get_prompt_hash(prompt: str, character: str) -> str:
    """Generate hash for prompt + character"""
    return hashlib.md5(f"{prompt}:{character}".encode()).hexdigest()

# Create global cache instance
cache = Cache()
