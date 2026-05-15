from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

from backend.app.ingestion.nodes.base import NodeType, NodeContext
from backend.app.ingestion.nodes import registry
from backend.app.ingestion.schemas import RawConversation, Message
from backend.app.models.chat_model import Conversation, ChatMessage


@registry.register
class SourceNode(NodeType):
    type_name = "source"
    display_name = "数据源"
    description = "从外部输入读取对话数据，转为统一的 RawConversation 格式"
    idempotent = True

    inputs = []
    outputs = ["raw_conversation"]

    class Params(BaseModel):
        source_type: str = "internal"  # "internal" | "link" | "pasted"
        paste_format: str = "generic"  # "generic" | "json"

    async def run(self, ctx: NodeContext, params: BaseModel) -> dict[str, Any]:
        source_type = ctx.blackboard.source_type or params.source_type


        if source_type == "internal":
            return await self._handle_internal(ctx)
        elif source_type == "link":
            return await self._handle_link(ctx)
        elif source_type == "pasted":
            return await self._handle_pasted(ctx, params.paste_format)
        else:
            raise ValueError(f"不支持的 source_type: {params.source_type}")


    async def _handle_internal(self,ctx: NodeContext) -> dict[str,Any]:
        conversation_id = ctx.blackboard.source_ref
        if not isinstance(conversation_id, str) or not conversation_id.strip():
            raise ValueError("internal 模式下 blackboard 需要提供 source_ref（conversation uuid）")

        try:
            conversation = await Conversation.get(uuid=conversation_id)
        except DoesNotExist:
            raise ValueError(f"对话不存在: {conversation_id}")

        db_messages = await ChatMessage.filter(
            conversation=conversation
        ).order_by("created_at")

        messages: list[Message] = []
        for msg in db_messages:
            text = self._extract_text(msg.content)
            if text:
                messages.append(Message(
                    role=msg.role,
                    content=text,
                    metadata={"message_uuid": str(msg.uuid)}
                ))

        raw = RawConversation(
            source_type="internal",
            source_ref=conversation_id,
            title=conversation.title,
            messages=messages,
            metadata={
                "model":conversation.model,
                "provider": conversation.provider
            }
        )

        return {"raw_conversation": raw.model_dump()}

    async def _handle_link(self,ctx: NodeContext) -> dict[str,Any]:
        source_input = ctx.blackboard.source_input
        if not isinstance(source_input, str) or not source_input.strip():
            raise ValueError("link 模式下 source_input 必须是非空 JSON 字符串")
        return self._parse_share_json(source_input)

    async def _handle_pasted(self, ctx: NodeContext, paste_format: str) -> dict[str, Any]:
        source_input = ctx.blackboard.source_input

        if not isinstance(source_input,str) or not source_input.strip():
            raise ValueError("pasted 模式下 source_input 必须是非空字符串")

        if paste_format == "json":
            return self._parse_share_json(source_input)
        else:
            raw = RawConversation(
                source_type="pasted",
                source_ref="pasted",
                messages=[Message(role="user", content=source_input.strip())],
                metadata={"unparsed": True},
            )
            return {"raw_conversation": raw.model_dump()}


    @staticmethod
    def _extract_text(content: Any) -> str:
        """从 ChatMessage.content（JSONB blocks 数组）提取纯文本。"""
        if isinstance(content, str):
            return content
        if not isinstance(content, list):
            return ""

        parts: list[str] = []
        for block in content:
            if not isinstance(block,dict):
                continue

            block_type = block.get("type")
            if block_type == 'text':
                text = block.get("text","")
                if text:
                    parts.append(text)
            elif block_type == "image":
                parts.append("[生成图片]")
        return "\n".join(parts)


    def _parse_share_json(self, source_input: str) -> dict[str, Any]:
        """解析 share JSON（link 和 pasted+json 共用）。"""
        try:
            data = json.loads(source_input)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败: {e}")

        title = data.get("snapshot_name","")
        raw_messages = data.get("chat_messages",[])

        messages: list[Message] = []
        for msg in raw_messages:
            sender = msg.get("sender", "")
            role = "user" if sender == "human" else "assistant"
            content_blocks = msg.get("content",[])
            text_parts = [
                block.get("text","")
                for block in content_blocks
                if isinstance(block,dict) and block.get("type") == "text"
            ]
            text = "\n".join(part for part in text_parts if part)
            if text:
                messages.append(Message(role=role, content=text))

        raw = RawConversation(
            source_type="link",
            source_ref=data.get("uuid", ""),
            title=title,
            messages=messages,
        )
        return {"raw_conversation": raw.model_dump()}











































