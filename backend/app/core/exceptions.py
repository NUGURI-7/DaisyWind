"""
自定义异常类
"""

from typing import Any, Optional


class AppApiException(Exception):
    """
    项目内基础异常
    """
    def __init__(self, code: int = 500, message: str = "Service error", data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)


class NotFound404(AppApiException):
    """
    404 未找到异常
    """
    def __init__(self, message: str = "资源不存在", code: int = 404, data: Any = None):
        super().__init__(code=code, message=message, data=data)


class AppAuthenticationFailed(AppApiException):
    """
    401 未认证(未登录)异常
    """
    def __init__(self, message: str = "未登录或登录已过期", code: int = 401, data: Any = None):
        super().__init__(code=code, message=message, data=data)


class AppUnauthorizedFailed(AppApiException):
    """
    403 未授权(没有权限)异常
    """
    def __init__(self, message: str = "权限不足", code: int = 403, data: Any = None):
        super().__init__(code=code, message=message, data=data)


class AppEmbedIdentityFailed(AppApiException):
    """
    460 嵌入身份认证失败
    """
    def __init__(self, message: str = "嵌入身份认证失败", code: int = 460, data: Any = None):
        super().__init__(code=code, message=message, data=data)


class AppChatNumOutOfBoundsFailed(AppApiException):
    """
    461 访问次数超过今日访问量
    """
    def __init__(self, message: str = "今日访问次数已用尽", code: int = 461, data: Any = None):
        super().__init__(code=code, message=message, data=data)


class ChatException(AppApiException):
    """
    500 聊天异常
    """
    def __init__(self, message: str = "聊天服务异常", code: int = 500, data: Any = None):
        super().__init__(code=code, message=message, data=data)


class ValidationException(AppApiException):
    """
    400 参数验证异常
    """
    def __init__(self, message: str = "参数验证失败", code: int = 400, data: Any = None):
        super().__init__(code=code, message=message, data=data)