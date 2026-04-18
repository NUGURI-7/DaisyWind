from pydantic_ai import RunContext
from tavily import AsyncTavilyClient

from backend.app.agents.deps import AgentDeps
from config import settings


async def tavily_web_search(
    ctx: RunContext[AgentDeps],
    query: str,
    search_depth: str = "basic"
) -> list[dict]:
    """Search the public web for up-to-date information using Tavily.

    Use this tool when the user asks about:
    - Current events, news, weather, or anything time-sensitive
    - Facts that may have changed since your training cutoff
    - Specific websites, products, or public figures you're not sure about

    For search_depth:
    - "basic": default, fast, suits most queries (1 credit)
    - "advanced": use when the question is complex, requires deeper research,
      or basic results are likely insufficient (2 credits, use sparingly)

    Do NOT use for:
    - Personal notes (use search_notes instead)
    - Math, reasoning, or tasks you can answer from general knowledge

    Args:
        query: A natural-language search query
        search_depth: "basic" or "advanced"

    Returns:
        A list of up to 10 results, each with title, url, and content snippet.
    """
    if not settings.TAVILY_API_KEY:
        return [{"error": "TAVILY_API_KEY not configured"}]

    client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
    response = await client.search(
        query=query,
        max_results=10,
        search_depth=search_depth,
    )

    results = response.get("results", [])
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": (r.get("content") or "")[:500],
        }
        for r in results  # 原来这里写的是 response，是个 bug
    ]