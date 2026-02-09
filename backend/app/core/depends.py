"""
@project: DaisyWind
@Author: niu
@file: depends
@date: 2026/2/9 21:01
@desc:
"""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.app.core.exceptions import AppAuthenticationFailed
from backend.app.core.security import verify_token
from backend.app.models import User
from backend.app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_service() -> UserService:
    return UserService()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    """
    从 JWT 解析当前登录用户
    """
    if not credentials:
        raise AppAuthenticationFailed(message="未提供认证token")

    payload = verify_token(credentials.credentials)
    if not payload:
        raise AppAuthenticationFailed(message="令牌无效或已过期")
    user_id = payload.get("sub")
    if not user_id:
        raise AppAuthenticationFailed(message="令牌格式错误")

    user = await User.filter(id=user_id).first()
    if not user:
        raise AppAuthenticationFailed(message="用户不存在")

    return user




