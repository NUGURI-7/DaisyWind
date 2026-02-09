from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from backend.app.api import api_router
from backend.app.core.exception_handlers import app_exception_handler, http_exception_handler, \
    validation_exception_handler, general_exception_handler
from backend.app.core.exceptions import AppApiException
from backend.app.core.redis import redis_client, RedisClient
from backend.app.db.mysql import MySQLClient
from config import settings
from contextlib import asynccontextmanager
from pathlib import Path
from starlette.exceptions import HTTPException as StarletteHTTPException

@asynccontextmanager
async def lifespan(app: FastAPI):
    # logger_init() 启动日志服务
    redis = RedisClient()
    await redis.connect()
    app.state.redis = redis # type: ignore

    # db_init() 链接数据库
    mysql = MySQLClient()
    await mysql.connect()
    # db_settings() 获取动态配置
    # service_init() 启动第三方服务
    # send_email() 发送email给程序维护者
    print("🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖")
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    print("✨ 初始化完成 ✨ ")
    yield

    # logger() 记录关闭日志
    await app.state.redis.close() # type: ignore
    await mysql.close()
    # db_close()
    # service_close()
    # send_email() 发送email给程序维护者

    print("👋 Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG_MODE,
    lifespan=lifespan
)


# 注册全局异常处理器
app.add_exception_handler(AppApiException, app_exception_handler)  # 自定义业务异常
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # HTTP 异常
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # 参数验证异常
app.add_exception_handler(Exception, general_exception_handler)  # 兜底异常处理
app.include_router(api_router, prefix="/api/nuguri")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
