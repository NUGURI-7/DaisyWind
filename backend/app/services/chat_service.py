"""
    @project: DaisyWind
    @Author: niu
    @file: chat_service.py
    @date: 2026/2/12 17:22
    @desc:
"""
from pydantic_ai import ModelMessage, ModelRequest, UserPromptPart, ModelResponse, TextPart

from backend.app.core.exceptions import NotFound404
from backend.app.models import User, Conversation, ChatMessage
from backend.app.schemas.chat_schema import MessageRole


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
    async def add_message(conversation: Conversation, role: MessageRole, content: str) -> ChatMessage:
        """添加一条消息"""
        message = await ChatMessage.create(
            conversation=conversation,
            role=role,
            content=content,
        )
        await conversation.save()
        return message

    @staticmethod
    async def get_chat_messages(conversation: Conversation) -> list[ChatMessage]:
        """获取对话的所有消息"""
        return await ChatMessage.filter(conversation=conversation).order_by("created_at").all()

    @staticmethod
    async def build_llm_messages(conversation: Conversation) -> list[ModelMessage]:
        """构建 PydanticAI 格式的 message_history。"""
        messages = await ChatService.get_chat_messages(conversation)
        result: list[ModelMessage] = []

        for msg in messages:
            if msg.role == "user":
                result.append(ModelRequest(parts=[UserPromptPart(content=msg.content)]))
            elif msg.role == "assistant":
                result.append(ModelResponse(parts=[TextPart(content=msg.content)]))

        return result

    @staticmethod
    async def update_title_from_first_message(conversation: Conversation) -> None:
        """用第一条 user 消息的前 30 字作为对话标题"""
        first_msg = await ChatMessage.filter(
            conversation=conversation, role=MessageRole.USER
        ).order_by("created_at").first()
        if first_msg:
            conversation.title = first_msg.content[:30]
            await conversation.save()

    @staticmethod
    async def get_or_create_conversation(
            uuid: str, user: User, provider: str = "deepseek", model: str = "deepseek-chat"
    ) -> tuple[Conversation, bool]:
        """获取或创建对话。返回 (conversation, created)。"""
        conversation = await Conversation.filter(uuid=uuid,user=user).first()
        if conversation:
            return conversation, False
        conversation = await Conversation.create(
            uuid=uuid, user=user, provider=provider, model=model
        )
        return conversation, True



