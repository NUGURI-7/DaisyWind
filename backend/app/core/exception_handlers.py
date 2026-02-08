"""
全局异常处理器
"""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.exceptions import AppApiException


async def app_exception_handler(request: Request, exc: AppApiException) -> JSONResponse:
    """
    处理自定义业务异常
    :param request:
    :param exc:
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": exc.data
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    处理 HTTP 异常（如 FastAPI 内部抛出的 HTTPException）
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理参数验证异常
    """
    errors = exc.errors()

    if errors:
        first_error = errors[0]
        field = first_error.get('loc', ['unknown'])[-1]
        msg = first_error.get('msg', 'parameter validate error')
        error_message = f"{field}:{msg}"
    else:
        error_message = "parameter validate error"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 400,
            "message": error_message,
            "data": errors
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理所有未捕获的异常
    """
    import traceback
    traceback.print_exc()  # 打印异常堆栈（开发环境）

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None
        }
    )