"""
    @project: DaisyWind
    @Author: niu
    @file: user_model.py
    @date: 2026/2/2 22:40
    @desc:
"""
from backend.app.db.base import BaseModel, UUIDModel, TimestampMixin
from tortoise import fields


class User(BaseModel, UUIDModel,TimestampMixin):
    username = fields.CharField(max_length=20, unique=True, description="用户名称", index=True)
    nick_name = fields.CharField(max_length=50, default="", description="昵称")
    rank_title = fields.CharField(max_length=50, default="", description="称号")
    email = fields.CharField(max_length=255, unique=True, description="邮箱", index=True)
    password = fields.CharField(max_length=128, null=True, description="密码")
    is_admin = fields.BooleanField(default=False, description="admin", index=True)


    def set_password(self, raw_password: str):

        from backend.app.core.security import get_password_hash

        self.password = get_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:

        from backend.app.core.security import verify_password
        if not self.password:
            return False
        return verify_password(raw_password,self.password)

    class Meta:
        table = "user"

    class PydanticMeta:
        exclude = "password"  # 序列化时排除密码


