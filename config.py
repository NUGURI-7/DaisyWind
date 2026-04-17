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

    # JWT 配置
    SECRET_KEY: str = "wK3_vHJkL9mNpQ2rS4tU5vW6xY7zA8bC9dE0fG1hI2j" # 必填，从环境变量读取
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 30  # 24小时

    # ==================== LLM Providers ====================
    DEEPSEEK_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DASHSCOPE_API_KEY: str = ""       # 阿里 Qwen
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_PROVIDER: str = "deepseek"
    DEFAULT_MODEL: str = "deepseek-chat"

    # 文件配置
    STATIC_DIR: str = "static"
    MEDIA_DIR: str = "data/media"  # 新增：用户上传的媒体文件存放路径

    # ==================== 对象存储 (R2/S3) 配置 ====================
    R2_ENDPOINT: str = ""           # 例: https://<AccountID>.r2.cloudflarestorage.com
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""        # 例: daisywind
    R2_PUBLIC_URL: str = ""         # 例: https://pub-xxx.r2.dev (留空表示拼接方式访问)


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

    # ==================== PostgreSQL 配置 ====================
    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    PG_USER: str = "postgres"
    PG_PASSWORD: str = ""
    PG_DATABASE: str = "daisywind"
    PG_POOL_MIN_SIZE: int = 1
    PG_POOL_MAX_SIZE: int = 10

    @property
    def pg_url(self) -> str:
        return f"postgres://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"

    # 配置模型设置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# 创建全局配置实例
settings = Settings()
