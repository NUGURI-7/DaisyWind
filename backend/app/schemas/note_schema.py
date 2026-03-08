"""
    @project: DaisyWind
    @Author: niu
    @file: note_schema.py
    @date: 2026/3/8 21:10
    @desc:
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NoteResponse(BaseModel):
    """笔记列表项（不含 content）"""
    uuid: UUID
    title: str
    preview: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NoteDetailResponse(NoteResponse):
    """笔记详情（含 content）"""
    content: str

class NoteUpdateRequest(BaseModel):
    """更新笔记请求体"""
    content: str = Field(..., description="笔记完整内容")