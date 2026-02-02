"""
    @project: Windify
    @Author: niu
    @file: user_model.py
    @date: 2026/2/2 22:40
    @desc:
"""
from backend.app.db.base import BaseModel, UUIDModel, TimestampMixin
from tortoise import fields
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel, UUIDModel,TimestampMixin):
    username = fields.CharField(max_length=20, unique=True, description="用户名称", index=True)
    email = fields.CharField(max_length=255, unique=True, description="邮箱", index=True)
    password = fields.CharField(max_length=128, null=True, description="密码")
    is_admin = fields.BooleanField(default=False, description="admin", index=True)


    def set_password(self, raw_password: str):

        self.password = pwd_context.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:

        if not self.password:
            return False
        return pwd_context.verify(raw_password,self.password)

    class Meta:
        table = "user"

    class PydanticMeta:
        exclude = "password"  # 序列化时排除密码


