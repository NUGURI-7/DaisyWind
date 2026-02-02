from tortoise import models, fields
import uuid_utils.compat as uuid

class BaseModel(models.Model):
    id = fields.BigIntField(pk=True, index=True)




class UUIDModel:
    uuid = fields.UUIDField(unique=True, pk=False, index=True,default=uuid.uuid7)




class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)
