"""
    @project: DaisyWind
    @file: sink.py
    @desc: Sink 节点：把最终草稿写入 Note 表，工作流终点。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from backend.app.ingestion.nodes import registry
from backend.app.ingestion.nodes.base import NodeType, NodeContext
from backend.app.models import Note


@registry.register
class SinkNode(NodeType):
    """终点节点：从 blackboard 读 draft 与 outline，落盘为 Note。"""

    type_name = "sink"
    display_name = "落盘"
    description = "把最终草稿写入 Note 表，结束工作流"
    idempotent = False

    inputs = ["draft", "outline"]
    outputs = ["note_id"]

    class Params(BaseModel):
        """Sink 当前无配置参数，保留空 Params 以符合 NodeType 协议。"""



    async def run(self, ctx: NodeContext, params: BaseModel) -> dict[str, Any]:
        draft: str = ctx.blackboard.get("draft","")
        outline: dict[str, Any] = ctx.blackboard.get("outline") or {}
        title: str = outline.get("title") or "Untitled"
        preview: str = draft[:100]

        note = await Note.create(
            user_id=ctx.user_id,
            title=title,
            content=draft,
            preview=preview
        )

        return {"note_id": note.id}



