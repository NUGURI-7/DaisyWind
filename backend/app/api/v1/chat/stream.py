"""
    @project: DaisyWind
    @Author: niu
    @file: stream.py.py
    @date: 2026/4/12 15:15
    @desc: SSE 流式对话端点
"""
from fastapi import APIRouter, Depends
from pydantic_ai import Agent, PartStartEvent, TextPart, PartDeltaEvent, TextPartDelta, PartEndEvent, \
    AgentRunResultEvent
from starlette.responses import StreamingResponse

from backend.app.agents.chat_agent import build_chat_agent
from backend.app.agents.deps import AgentDeps
from backend.app.agents.pricing import calc_cost
from backend.app.core.depends import get_current_user
from backend.app.models import User, Conversation
from backend.app.schemas.chat_schema import ChatRequest, MessageRole
from backend.app.services.chat_service import ChatService
from backend.app.services.sse import sse_event

router = APIRouter()


async def stream_generator(
        agent: Agent,
        deps: AgentDeps,
        user_input: str,
        llm_messages: list[dict],
        conversation: Conversation,
        created: bool,
        request: ChatRequest
):
    """SSE async generator：驱动 Agent 流式输出并转换为 SSE 事件。"""
    assistant_text = ""

    yield sse_event("message_start",{
        "conversation_uuid": str(conversation.uuid),
        "message_uuid": request.message_uuid,
        "model": request.model,
        "provider": request.provider
    })

    try:
        async for event in agent.run_stream_events(
            user_input,
            deps=deps,
            message_history=llm_messages
        ):
            if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
                yield sse_event("content_block_start", {
                    "index": event.index,
                    "type": "text"
                })
                if event.part.content:
                    assistant_text += event.part.content
                    yield sse_event("content_block_delta",{
                        "index": event.index,
                        "type": "text_delta",
                        "text": event.part.content
                    })
            # TODO P1: handle ThinkingPart → content_block_start(type="thinking")
            # TODO P1: handle ToolCallPart → tool_use_start
            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):

                assistant_text += event.delta.content_delta
                yield sse_event("content_block_delta", {
                    "index": event.index,
                    "type": "text_delta",
                    "text": event.delta.content_delta
                })
            elif isinstance(event,PartEndEvent):
                yield sse_event("content_block_stop", {
                    "index": event.index
                })
            elif isinstance(event, AgentRunResultEvent):
                usage = event.result.usage()
                cost = calc_cost(request.model, usage.input_tokens,usage.output_tokens)
                yield sse_event("message_delta", {
                    "stop_reason": "end_turn",
                    "usage": {
                        "input_tokens": usage.input_tokens,
                        "output_tokens": usage.output_tokens,
                        "cost": cost
                    }
                })

        yield sse_event("message_stop", {})

    except Exception as e:
        yield sse_event("error", {
            "code": "internal_error",
            "message": str(e)
        })

    finally:
        # 持久化 assistant message
        if assistant_text:
            await ChatService.add_message(
                conversation, MessageRole.ASSISTANT, assistant_text
            )

            if created:
                await ChatService.update_title_from_first_message(conversation)


@router.post("/send")
async def send_message(request: ChatRequest, user: User = Depends(get_current_user)):
    """发送消息，返回 SSE 流。"""

    conversation, created = await ChatService.get_or_create_conversation(
        uuid=request.conversation_uuid,
        user=user,
        provider=request.provider,
        model=request.model
    )

    await ChatService.add_message(conversation, MessageRole.USER, request.content)

    llm_messages = await ChatService.build_llm_messages(conversation)

    agent = build_chat_agent(request.provider, request.model)
    deps = AgentDeps(user=user, conversation=conversation)

    return StreamingResponse(
        stream_generator(
            agent=agent,
            deps=deps,
            user_input=request.content,
            llm_messages=llm_messages[:-1], # 最后一条是刚存的 user msg，已作为 user_input 传入
            conversation=conversation,
            created=created,
            request=request
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )









