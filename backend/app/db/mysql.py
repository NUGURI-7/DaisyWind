from tortoise import Tortoise, connections
from tortoise.contrib.fastapi import RegisterTortoise

from config import settings

# Tortoise ORM 配置字典
TORTOISE_CONFIG = {
    'connections': {
        'default': {  # 连接名称
            'engine': 'tortoise.backends.mysql',  # MySQL 后端引擎
            'credentials': {
                'host': settings.MYSQL_HOST,
                'port': settings.MYSQL_PORT,
                'user': settings.MYSQL_USER,
                'password': settings.MYSQL_PASSWORD,
                'database': settings.MYSQL_DATABASE,
                'minsize': settings.MYSQL_POOL_MIN_SIZE,  # 连接池最小连接数
                'maxsize': settings.MYSQL_POOL_MAX_SIZE,  # 连接池最大连接数
                'echo': settings.MYSQL_ECHO,  # 是否打印 SQL 日志
                'charset': 'utf8mb4',  # 字符集
                'connect_timeout': 10,  # 连接超时时间（秒）
                'pool_recycle': 300,  # 每 5 分钟回收空闲连接，防止 MySQL 关掉后报 Lost connection
            }
        },
    },
    'apps': {
        'models': {  # 应用名称（可以自定义，比如 'DaisyWind'）
            'models': [
                'backend.app.models',
                "backend.app.models.chat_model"
            ],  # 模型所在的模块路径
            'default_connection': 'default',  # 使用的连接名称
        },
    },
    'use_tz': False,  # 是否使用时区（False 表示不使用时区）
    'timezone': 'Asia/Shanghai',  # 时区设置
}

class MySQLClient:


    def __init__(self):
        self._initialized: bool = False

    async def connect(self):

        if self._initialized:
            return

        try:
            await Tortoise.init(config=TORTOISE_CONFIG)

            # if settings.DEBUG_MODE:
            #     await Tortoise.generate_schemas()
            # ❌ 注释掉自动建表（改用 Aerich）
            self._initialized=True
            print("✅ MySQL 连接成功")
        except Exception as e:
            print(f"❌ MySQL 连接失败: {e}")
            raise

    async def close(self):

        if self._initialized:
            await connections.close_all()
            self._initialized = False
            print("👋 MySQL 连接已关闭")

    @property
    def is_connected(self):
        return self._initialized

mysql_client = MySQLClient()
