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
from backend.app.tools.brave_web_search_tool import brave_web_search
from backend.app.tools.notes_tool import search_notes
from backend.app.tools.tavily_web_search_tool import tavily_web_search

SYSTEM_PROMPT = """\
You are a helpful AI assistant.

Respond in the language the user is using.
Use Markdown formatting where appropriate, and always specify the language in code blocks.

You have access to tools that let you search the user's personal data. Call a
tool only when it is genuinely useful — for simple small talk, general
knowledge, or content you already know, answer directly without using tools.

When the user asks about their own notes, past entries, or content they have
written, use the `search_notes` tool to look them up by keyword.

When the user asks about time-sensitive information (current news, weather,
prices, recent releases) or facts that may have changed since your training
cutoff, use the `tavily_web_search` or `brave_web_search` tool to search the public web. Do not use
it for questions you can confidently answer from general knowledge.
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
    agent = Agent(
        model,
        system_prompt=SYSTEM_PROMPT,
        deps_type=AgentDeps,
    )

    agent.tool(search_notes)
    agent.tool(tavily_web_search)
    agent.tool(brave_web_search)

    return agent