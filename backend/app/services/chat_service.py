"""
    @project: DaisyWind
    @Author: niu
    @file: chat_service.py
    @date: 2026/2/12 17:22
    @desc:
"""
from pydantic_ai import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)

from backend.app.core.exceptions import NotFound404
from backend.app.models import User, Conversation, ChatMessage
from backend.app.schemas.chat_schema import MessageRole, ContentBlock


class ChatService:

    @staticmethod
    async def create_conversation(user: User, model: str = "deepseek-chat") -> Conversation:
        """创建新对话"""
        conversation = await Conversation.create(user=user, model=model)
        return conversation

    @staticmethod
    async def list_conversations(user: User) -> list[Conversation]:
        """获取用户的对话列表"""
        return await Conversation.filter(user=user).order_by("-updated_at").all()

    @staticmethod
    async def get_conversation(uuid: str, user: User) -> Conversation:
        """获取单个对话，校验归属"""
        conversation = await Conversation.filter(uuid=uuid, user=user).first()
        if not conversation:
            raise NotFound404(message="Conversation not found")
        return conversation

    @staticmethod
    async def delete_conversation(uuid: str, user: User) -> None:
        """删除对话（级联删除消息）"""
        conversation = await ChatService.get_conversation(uuid, user)
        await conversation.delete()

    @staticmethod
    async def add_message(conversation: Conversation, role: MessageRole, content: list[ContentBlock]) -> ChatMessage:
        """添加一条消息"""
        message = await ChatMessage.create(
            conversation=conversation,
            role=role,
            content=[block.model_dump() for block in content],
        )
        await conversation.save()
        return message

    @staticmethod
    async def get_chat_messages(conversation: Conversation) -> list[ChatMessage]:
        """获取对话的所有消息"""
        return await ChatMessage.filter(conversation=conversation).order_by("created_at").all()

    @staticmethod
    async def build_llm_messages(conversation: Conversation) -> list[ModelMessage]:
        """构建 PydanticAI 格式的 message_history。

    DB 里的 content 是 block 数组 [{type:text|tool_use, ...}]，
    按 role 和 block type 映射成对应的 PydanticAI Part。
    """
        messages = await ChatService.get_chat_messages(conversation)
        result: list[ModelMessage] = []

        for msg in messages:

            blocks = msg.content or []

            if msg.role == "user":
                # user 目前只会有 text block
                text = "".join(b.get("text", "") for b in blocks if b.get('type') == "text")
                result.append(ModelRequest(parts=[UserPromptPart(content=text)]))

            elif msg.role == "assistant":
                response_parts = []
                tool_returns: list[ToolReturnPart] = []

                for b in blocks:
                    b_type = b.get("type")
                    if b_type == "text":
                        response_parts.append(TextPart(content=b.get("text", "")))
                    elif b_type == "tool_use":
                        # assistant 这一轮发起的 tool 调用
                        response_parts.append(ToolCallPart(
                            tool_call_id=b["id"],
                            tool_name=b["name"],
                            args=b.get("input") or {}
                        ))
                        # 对应的返回结果作为下一条 ModelRequest 注入
                        tool_returns.append(ToolReturnPart(
                            tool_call_id=b["id"],
                            tool_name=b["name"],
                            content=b.get("output")
                        ))

                if response_parts:
                    result.append(ModelResponse(parts=response_parts))
                if tool_returns:
                    result.append(ModelRequest(parts=tool_returns))

        return result

    @staticmethod
    async def update_title_from_first_message(conversation: Conversation) -> None:
        """用第一条 user 消息的前 30 字作为对话标题"""
        first_msg = await ChatMessage.filter(
            conversation=conversation, role=MessageRole.USER
        ).order_by("created_at").first()
        if not first_msg:
            return
        blocks = first_msg.content or []
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        conversation.title = text[:30] if text else "New chat"

        await conversation.save()

    @staticmethod
    async def get_or_create_conversation(
            uuid: str, user: User, provider: str = "deepseek", model: str = "deepseek-chat"
    ) -> tuple[Conversation, bool]:
        """获取或创建对话。返回 (conversation, created)。"""
        conversation = await Conversation.filter(uuid=uuid, user=user).first()
        if conversation:
            return conversation, False
        conversation = await Conversation.create(
            uuid=uuid, user=user, provider=provider, model=model
        )
        return conversation, True
