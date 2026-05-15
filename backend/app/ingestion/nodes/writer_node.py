"""
    @project: DaisyWind
    @file: writer_node.py
    @desc: Writer 节点：调 LLM 将对话整理成 Markdown 笔记。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent

from backend.app.ingestion.nodes import registry
from backend.app.ingestion.nodes.base import NodeType, NodeContext
from backend.app.ingestion.schemas import RawConversation
from backend.app.agents.providers import build_model

SYSTEM_PROMPT = """\
你是一个专业的笔记整理助手。你的任务是将用户和 AI 之间的对话整理成一篇结构清晰、重点突出的 Markdown 笔记。

要求：
1. 提取对话中的核心知识点和关键信息
2. 用清晰的层级结构组织内容（标题、小节、列表等）
3. 保留重要的代码示例和技术细节
4. 去除对话中的闲聊、重复和无关内容
5. 笔记应该是独立可读的，即使脱离原始对话也能理解
6. 使用与对话相同的语言撰写笔记
"""


class NoteOutline(BaseModel):
    """笔记元信息。"""
    title: str
    summary: str
    tags: list[str]


class NoteDraft(BaseModel):
    """Writer 节点的结构化输出。"""
    draft: str
    outline: NoteOutline


@registry.register
class WriterNode(NodeType):
    type_name = "writer"
    display_name = "笔记撰写"
    description = "调用 LLM 将对话内容整理成结构化的 Markdown 笔记"
    idempotent = False

    inputs = ["raw_conversation"]
    outputs = ["draft", "outline"]

    class Params(BaseModel):
        model: str = "deepseek-chat"
        provider: str = "deepseek"

    async def run(self, ctx: NodeContext, params: BaseModel) -> dict[str, Any]:
        raw_data = ctx.blackboard.raw_conversation
        if not raw_data:
            raise ValueError("blackboard 中缺少 raw_conversation")

        raw = RawConversation.model_validate(raw_data)
        if not raw.messages:
            raise ValueError("raw_conversation 中没有消息")

        prompt = self._build_prompt(raw)

        llm_model = build_model(params.provider, params.model)
        agent = Agent(
            llm_model,
            system_prompt=SYSTEM_PROMPT,
            output_type=NoteDraft,
        )

        result = await agent.run(prompt)
        output: NoteDraft = result.output

        return {
            "draft": output.draft,
            "outline": output.outline.model_dump(),
        }

    @staticmethod
    def _build_prompt(raw: RawConversation) -> str:
        """将 RawConversation 转换为 LLM 可读的文本 prompt。"""
        parts: list[str] = []
        if raw.title:
            parts.append(f"对话标题：{raw.title}\n")

        for msg in raw.messages:
            label = "用户" if msg.role == "user" else "AI 助手"
            parts.append(f"【{label}】\n{msg.content}\n")

        return "\n".join(parts)