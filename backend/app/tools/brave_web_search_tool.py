import httpx
from pydantic_ai import RunContext

from backend.app.agents.deps import AgentDeps
from config import settings


async def brave_web_search(
    ctx: RunContext[AgentDeps],
    query: str,
) -> list[dict]:
    """Search the public web for up-to-date information using Brave Search.

    Use this tool when the user asks about:
    - Current events, news, weather, or anything time-sensitive
    - Facts that may have changed since your training cutoff
    - Specific websites, products, or public figures you're not sure about

    Do NOT use for:
    - Personal notes (use search_notes instead)
    - Math, reasoning, or tasks you can answer from general knowledge

    Args:
        query: A natural-language search query

    Returns:
        A list of up to 10 results, each with title, url, and content snippet.
    """
    if not settings.BRAVE_API_KEY:
        return [{"error": "BRAVE_API_KEY not configured"}]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "X-Subscription-Token": settings.BRAVE_API_KEY,
                "Accept": "application/json",
            },
            params={"q": query, "count": 10},
        )
        response.raise_for_status()
        data = response.json()

    results = data.get("web", {}).get("results", [])
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": (r.get("description") or "")[:500],
        }
        for r in results
    ]