import pytest
import asyncio
from app.core.rate_limiter import (
    InMemoryRateLimiter,
    RateLimitConfig,
    ScanQueueManager,
)


@pytest.fixture
def limiter():
    return InMemoryRateLimiter()


@pytest.fixture
def queue_manager():
    return ScanQueueManager(max_concurrent=2, max_queue_size=5)


@pytest.mark.asyncio
async def test_rate_limiter_allows_within_limit(limiter):
    config = RateLimitConfig(requests=5, window_seconds=60)
    
    for i in range(5):
        allowed, _ = await limiter.is_allowed("test_key", config)
        assert allowed is True


@pytest.mark.asyncio
async def test_rate_limiter_blocks_over_limit(limiter):
    config = RateLimitConfig(requests=3, window_seconds=60)
    
    for _ in range(3):
        await limiter.is_allowed("test_key", config)
    
    allowed, retry_after = await limiter.is_allowed("test_key", config)
    assert allowed is False
    assert retry_after > 0


@pytest.mark.asyncio
async def test_rate_limiter_burst(limiter):
    config = RateLimitConfig(requests=2, window_seconds=60, burst=2)
    
    for i in range(4):
        allowed, _ = await limiter.is_allowed("burst_key", config)
        assert allowed is True
    
    allowed, _ = await limiter.is_allowed("burst_key", config)
    assert allowed is False


@pytest.mark.asyncio
async def test_rate_limiter_separate_keys(limiter):
    config = RateLimitConfig(requests=1, window_seconds=60)
    
    allowed1, _ = await limiter.is_allowed("key1", config)
    allowed2, _ = await limiter.is_allowed("key2", config)
    
    assert allowed1 is True
    assert allowed2 is True


@pytest.mark.asyncio
async def test_queue_manager_concurrent_limit(queue_manager):
    acquired = await queue_manager.acquire()
    assert acquired is True
    assert queue_manager.current_load["running"] == 1
    
    acquired2 = await queue_manager.acquire()
    assert acquired2 is True
    assert queue_manager.current_load["running"] == 2


@pytest.mark.asyncio
async def test_queue_manager_release(queue_manager):
    await queue_manager.acquire()
    assert queue_manager.current_load["running"] == 1
    
    await queue_manager.release()
    assert queue_manager.current_load["running"] == 0


@pytest.mark.asyncio
async def test_queue_manager_load_info(queue_manager):
    load = queue_manager.current_load
    
    assert "running" in load
    assert "queued" in load
    assert "max_concurrent" in load
    assert "max_queue" in load
    assert load["max_concurrent"] == 2
    assert load["max_queue"] == 5
