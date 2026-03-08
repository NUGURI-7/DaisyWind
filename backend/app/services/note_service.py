"""
    @project: DaisyWind
    @Author: niu
    @file: note_service.py
    @date: 2026/3/8 18:33
    @desc:
"""
import re
from datetime import datetime, timezone

from backend.app.models import Note
from backend.app.core.exceptions import NotFound404


def _extract_title(content: str) -> str:
    match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"

def _extract_preview(content: str) -> str:
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            clean = re.sub(r'[*_`\[\]()!\->#]', '', stripped).strip()
            return clean[:100]
    return ""



class NoteService:

    async def get_list(self, user_id: int) -> list[None]:

        return await Note.filter(
            user_id=user_id,
            deleted_at=None
        ).order_by('-updated_at').only(
            'id','uuid','title','preview','created_at','updated_at'
        )

    async def get_one(self, note_uuid: str, user_id:int) -> Note:

        note = await Note.filter(
            uuid=note_uuid,user_id=user_id,deleted_at=None
        ).first()

        if not note:
            raise NotFound404(message='Note not found')
        return note

    async def create(self, user_id: int) -> Note:
        note = await Note.create(
            user_id=user_id,
            content="# Untitled\n",
            title="Untitled",
            preview="",
        )
        return note

    async def update(self, note_uuid: str,user_id: int,content: str) -> Note:

        note = await self.get_one(note_uuid,user_id)
        note.content = content
        note.title = _extract_title(content)
        note.preview = _extract_preview(content)

        await note.save(update_fields=['content','title','preview','updated_at'])
        return note

    async def delete(self, note_uuid: str,user_id: int) -> None:
        note = await self.get_one(note_uuid,user_id)
        note.deleted_at = datetime.now(timezone.utc)
        await note.save(update_fields=['deleted_at'])

        updated = Note.filter(uuid=note_uuid,user_id=user_id,deleted_at=None).update(
            deleted_at=datetime.now(timezone.utc)
        )
        if not updated:
            raise NotFound404(message="Note not found")

