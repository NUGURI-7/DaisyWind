"""
    @project: DaisyWind
    @Author: niu
    @file: postgresql.py
    @date: 2026/3/6 10:06
    @desc:
"""
from tortoise import Tortoise, connections

from config import settings

# Tortoise ORM 配置字典
TORTOISE_CONFIG = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',  # PG 后端引擎
            'credentials': {
                'host': settings.PG_HOST,
                'port': settings.PG_PORT,
                'user': settings.PG_USER,
                'password': settings.PG_PASSWORD,
                'database': settings.PG_DATABASE,
                'minsize': settings.PG_POOL_MIN_SIZE,  # 连接池最小连接数
                'maxsize': settings.PG_POOL_MAX_SIZE,  # 连接池最大连接数
            }
        },
    },
    'apps': {
        'models': {
            'models': [
                'backend.app.models',
                "backend.app.models.chat_model"
            ],
            'default_connection': 'default',
        },
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai',
}

class PostgreSQLClient:

    def __init__(self):
        self._initialized: bool = False

    async def connect(self):

        if self._initialized:
            return

        try:
            await Tortoise.init(config=TORTOISE_CONFIG)
            self._initialized = True
            print("✅ PostgreSQL 连接成功")
        except Exception as e:
            print(f"❌ PostgreSQL 连接失败: {e}")
            raise

    async def close(self):

        if self._initialized:
            await connections.close_all()
            self._initialized = False
            print("👋 PostgreSQL 连接已关闭")

    @property
    def is_connected(self):
        return self._initialized

pg_client = PostgreSQLClient()
