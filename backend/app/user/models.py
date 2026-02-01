"""
    @project: Windify
    @Author: niu
    @file: models.py.py
    @date: 2026/2/1 18:09
    @desc:
"""
from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.UUIDField(primary_key=True, generated=True)