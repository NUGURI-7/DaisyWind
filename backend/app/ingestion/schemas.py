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


class Blackboard(BaseModel):
    """Ingestion 工作流黑板，所有节点间共享的类型化状态。"""
    # API 层写入（初始输入）
    source_type: str
    source_ref: str
    source_input: str | None = None
    paste_format: str | None = None

    # source_node 输出
    raw_conversation: dict[str, Any] | None = None

    # writer_node 输出
    draft: str | None = None
    outline: dict[str, Any] | None = None

    # sink_node 输出
    note_uuid: str | None = None