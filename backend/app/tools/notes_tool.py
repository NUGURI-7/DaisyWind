"""
    @project: DaisyWind
    @file: notes_tool.py
    @desc: Notes 搜索 Tool —— 让 Agent 可以在当前用户的 Notes 里做关键词搜索
"""
from pydantic_ai import RunContext

from backend.app.agents.deps import AgentDeps
from backend.app.models import Note



async  def search_notes(ctx: RunContext[AgentDeps], query: str) -> list[dict]:
    """Search the current user's personal notes by keyword.

    Use this tool when the user asks about something they previously wrote,
    saved, or recorded in their own notes. The query is matched against
    the note content (case-insensitive substring match). Returns up to 5
    most recently updated matching notes.

    Args:
        query: Keyword or phrase to search for inside note content.

    Returns:
        A list of matching notes, each with uuid / title / preview.
        Empty list if no match.
    """
    user = ctx.deps.user

    notes: list[Note] = (
        await Note.filter(
            user=user,
            deleted_at=None,
            content__icontains=query,
        )
        .order_by("-updated_at")
        .limit(5)
        .all()
    )

    return [
        {
            "title": n.title,
            "content": n.content,
        }
        for n in notes
    ]
