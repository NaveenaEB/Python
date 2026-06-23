import redis
import os
import logging

# In production, these should be in a .env file
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

logger = logging.getLogger("uvicorn.error")


class SafeRedisClient:
    def __init__(self):
        self._client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self._connection_warning_logged = False

    def _handle_error(self, exc: redis.RedisError):
        if not self._connection_warning_logged:
            logger.warning("Redis cache unavailable: %s", exc)
            self._connection_warning_logged = True

    def get(self, key: str):
        try:
            return self._client.get(key)
        except redis.RedisError as exc:
            self._handle_error(exc)
            return None

    def setex(self, key: str, expiry: int, value: str):
        try:
            return self._client.setex(key, expiry, value)
        except redis.RedisError as exc:
            self._handle_error(exc)
            return False

    def delete(self, *keys: str):
        try:
            return self._client.delete(*keys)
        except redis.RedisError as exc:
            self._handle_error(exc)
            return 0

    def delete_pattern(self, pattern: str):
        try:
            keys = list(self._client.scan_iter(match=pattern))
            if keys:
                return self._client.delete(*keys)
            return 0
        except redis.RedisError as exc:
            self._handle_error(exc)
            return 0


redis_client = SafeRedisClient()
