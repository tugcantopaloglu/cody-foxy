import time
import asyncio
from typing import Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps
from fastapi import Request, HTTPException, status
import redis.asyncio as redis
from .config import settings


@dataclass
class RateLimitConfig:
    requests: int
    window_seconds: int
    burst: int = 0


class RateLimitExceeded(HTTPException):
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )


class InMemoryRateLimiter:
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str, config: RateLimitConfig) -> Tuple[bool, int]:
        async with self._lock:
            now = time.time()
            window_start = now - config.window_seconds
            
            self._requests[key] = [t for t in self._requests[key] if t > window_start]
            
            max_requests = config.requests + config.burst
            
            if len(self._requests[key]) >= max_requests:
                oldest = min(self._requests[key]) if self._requests[key] else now
                retry_after = int(oldest + config.window_seconds - now) + 1
                return False, max(retry_after, 1)
            
            self._requests[key].append(now)
            return True, 0


class RedisRateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def is_allowed(self, key: str, config: RateLimitConfig) -> Tuple[bool, int]:
        now = time.time()
        window_key = f"rate:{key}:{int(now // config.window_seconds)}"
        
        pipe = self.redis.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, config.window_seconds + 1)
        results = await pipe.execute()
        
        count = results[0]
        max_requests = config.requests + config.burst
        
        if count > max_requests:
            retry_after = config.window_seconds - int(now % config.window_seconds)
            return False, max(retry_after, 1)
        
        return True, 0


class RateLimiter:
    _instance: Optional['RateLimiter'] = None

    def __init__(self):
        if settings.REDIS_URL:
            try:
                self._backend = RedisRateLimiter(settings.REDIS_URL)
            except Exception:
                self._backend = InMemoryRateLimiter()
        else:
            self._backend = InMemoryRateLimiter()

    @classmethod
    def get_instance(cls) -> 'RateLimiter':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def check(self, key: str, config: RateLimitConfig) -> None:
        allowed, retry_after = await self._backend.is_allowed(key, config)
        if not allowed:
            raise RateLimitExceeded(retry_after)


RATE_LIMITS = {
    "scan_upload": RateLimitConfig(requests=10, window_seconds=3600, burst=2),
    "scan_github": RateLimitConfig(requests=20, window_seconds=3600, burst=5),
    "api_default": RateLimitConfig(requests=100, window_seconds=60, burst=20),
    "ai_analysis": RateLimitConfig(requests=50, window_seconds=3600, burst=10),
}


def rate_limit(limit_name: str = "api_default"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Optional[Request] = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request:
                client_ip = request.client.host if request.client else "unknown"
                key = f"{limit_name}:{client_ip}"
                
                limiter = RateLimiter.get_instance()
                config = RATE_LIMITS.get(limit_name, RATE_LIMITS["api_default"])
                await limiter.check(key, config)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class ScanQueueManager:
    def __init__(self, max_concurrent: int = 5, max_queue_size: int = 100):
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        self._running = 0
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        async with self._lock:
            if self._running >= self.max_concurrent:
                if self._queue.full():
                    return False
                await self._queue.put(asyncio.Event())
                event = await self._queue.get()
                await event.wait()
            
            self._running += 1
            return True

    async def release(self) -> None:
        async with self._lock:
            self._running -= 1
            
            if not self._queue.empty():
                try:
                    event = self._queue.get_nowait()
                    event.set()
                except asyncio.QueueEmpty:
                    pass

    @property
    def current_load(self) -> dict:
        return {
            "running": self._running,
            "queued": self._queue.qsize(),
            "max_concurrent": self.max_concurrent,
            "max_queue": self.max_queue_size,
        }


scan_queue = ScanQueueManager(max_concurrent=5, max_queue_size=100)
