from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基础配置
    APP_NAME: str = "Windify"
    APP_VERSION: str = "0.1.0"
    DEBUG_MODE: bool = True

    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = True

    # 文件配置
    STATIC_DIR: str = "static"

    # ==================== Redis 配置 ====================
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = 123456
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 10

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ==================== MySQL 配置 ====================
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "windify"
    MYSQL_POOL_MIN_SIZE: int = 1
    MYSQL_POOL_MAX_SIZE: int = 10
    MYSQL_ECHO: bool = False

    @property
    def mysql_url(self) -> str:
        return f"mysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # 配置模型设置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# 创建全局配置实例
settings = Settings()
