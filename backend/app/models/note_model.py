"""
    @project: DaisyWind
    @Author: niu
    @file: note_model.py
    @date: 2026/3/8 18:21
    @desc:
"""
from tortoise import fields
from backend.app.db.base import BaseModel, UUIDModel, TimestampMixin


class Note(BaseModel, UUIDModel, TimestampMixin):
    user = fields.ForeignKeyField("models.User", related_name="notes")
    content = fields.TextField(default="")
    title = fields.CharField(max_length=255, default="Untitled")
    preview = fields.CharField(max_length=100, default="")
    deleted_at = fields.DatetimeField(null=True, default=None)


    class Meta:
        table = "note"
        indexes = [("user_id", "deleted_at", "updated_at")]
