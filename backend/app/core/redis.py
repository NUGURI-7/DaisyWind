"""
    @project: Windify
    @Author: niu
    @file: redis.py.py
    @date: 2026/1/31 20:36
    @desc:
"""
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError

redis_pool = redis.ConnectionPool(

)