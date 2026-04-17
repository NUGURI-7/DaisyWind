"""
    @project: DaisyWind
    @Author: niu
    @file: chat_schema.py
    @date: 2026/2/12 17:10
    @desc:
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    """发送消息请求"""
    conversation_uuid: str
    message_uuid: str # 前端生成 uuid
    content: str
    provider: str = "deepseek"
    model: str = "deepseek-chat"

class ConversationOut(BaseModel):
    """对话列表项"""
    uuid: UUID
    title: str
    model: str
    provider: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessageOut(BaseModel):
    """消息"""
    uuid: UUID
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationDetail(BaseModel):
    """对话详情（含消息列表"""
    uuid: UUID
    title: str
    model_str: str
    provider: str
    messages: list[MessageOut]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
