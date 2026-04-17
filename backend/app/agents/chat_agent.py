"""
    @project: DaisyWind
    @Author: niu
    @file: chat_agent.py
    @date: 2026/4/10 16:05
    @desc:
"""

from pydantic_ai import Agent

from backend.app.agents.deps import AgentDeps
from backend.app.agents.providers import build_model

SYSTEM_PROMPT = """\
You are a helpful AI assistant.
Respond in the language the user is using.
Use Markdown formatting where appropriate, and always specify the language in code blocks.
"""


def build_chat_agent(provider: str, model_name: str) -> Agent[AgentDeps, str]:
    """构造一个基础 Chat Agent（无 Tool）。

    Args:
        provider: 厂商标识
        model_name: 模型名

    Returns:
        配置好的 PydanticAI Agent，output 类型为 str（纯文本）
    """
    model = build_model(provider, model_name)
    return Agent(
        model,
        system_prompt=SYSTEM_PROMPT,
        deps_type=AgentDeps,
    )