"""
    @project: Windify
    @Author: niu
    @file: redis.py.py
    @date: 2026/1/31 20:36
    @desc:
"""
from typing import Optional
from redis import asyncio as aioredis
from redis.asyncio import ConnectionPool

from config import settings


class RedisClient:
    """Redis 客户端封装类"""

    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[aioredis.Redis] = None


    async def connect(self):
        """初始化redis连接池和客户端"""

        self._pool = ConnectionPool.from_url(
            settings.REDIS_HOST,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_response=True
        )

        self._client = aioredis.Redis(connection_pool=self._pool)

        try:
            await self._client.ping()
            print("✅ Redis ok")
        except Exception as e:
            print(f"❌ Redis connection error: {e}")
            raise

    async def close(self):
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        print("👋 Redis 连接已关闭")

    @property
    def client(self) -> aioredis.Redis:
        if not self._client:
            raise RuntimeError("Redis 客户端未初始化，请先调用 connect()")

        return self._client


redis_client = RedisClient()


async def get_redis() -> aioredis.Redis:
    """
    FastAPI 依赖注入函数

    用法：
    from backend.app.core.redis import get_redis
    from fastapi import Depends

    @router.get("/test")
    async def test(redis: Redis = Depends(get_redis)):
        await redis.set("key", "value")
    """
    return redis_client.client

