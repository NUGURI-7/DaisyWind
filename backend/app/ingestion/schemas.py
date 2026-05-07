from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str # "user" | "assistant" | "system"
    content: str
    metadata: dict[str,Any] = Field(default_factory=dict)




class RawConversation(BaseModel):
    """Source 节点的输出，blackboard 上 raw_conversation 的结构。"""
    source_type: str                # "pasted" | "internal" | "deepseek_share"
    source_ref: str                 # 原始标识（URL / conversation_id / "pasted"）
    title: str = ""
    messages: list[Message] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

