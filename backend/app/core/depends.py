"""
@project: DaisyWind
@Author: niu
@file: depends
@date: 2026/2/9 21:01
@desc:
"""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

from backend.app.core.exceptions import AppAuthenticationFailed, NotFound404
from backend.app.core.security import verify_token
from backend.app.models import User
from backend.app.models.chat_model import Conversation
from backend.app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_service() -> UserService:
    return UserService()


# 全局通用 API 鉴权（仅限 Header）
async def get_current_user(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> User:
    """
    标准 API 鉴权：严格要求 Authorization Header，防御 CSRF
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


# 专供图片等静态资源鉴权（支持 Cookie）
async def get_current_user_from_cookie(request: Request) -> User:

   token = request.cookies.get('access_token')

   if not token:
        # 兼容部分直接使用 Axios 请求资源的场景
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

   if not token:
       raise AppAuthenticationFailed(message="未提供认证token或Cookie")

   payload = verify_token(token)
   if not payload:
       raise AppAuthenticationFailed(message="令牌无效或已过期")

   user_id = payload.get("sub")
   if not user_id:
       raise AppAuthenticationFailed(message="令牌格式错误")

   user = await User.filter(id=user_id).first()
   if not user:
       raise AppAuthenticationFailed(message="用户不存在")

   return user



async def get_conversation_or_404(
    uuid: str,
    user: User = Depends(get_current_user),
) -> Conversation:
    """获取对话，同时校验归属当前用户。"""
    conversation = await Conversation.filter(uuid=uuid,user=user).first()
    if not conversation:
        raise NotFound404(message="Conversation not found")
    return conversation