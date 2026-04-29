from tortoise import models, fields
import uuid_utils.compat as uuid

class BaseModel(models.Model):
    id = fields.BigIntField(pk=True)

    class Meta:
        abstract = True


class UUIDModel:
    uuid = fields.UUIDField(unique=True, pk=False,default=uuid.uuid7)




class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
