"""
    @project: DaisyWind
    @Author: niu
    @file: note.py.py
    @date: 2026/3/8 21:14
    @desc:
"""

from fastapi import APIRouter, Depends

from backend.app.core.depends import get_current_user
from backend.app.core.response import success
from backend.app.models import User
from backend.app.schemas.note_schema import NoteResponse, NoteDetailResponse, NoteUpdateRequest
from backend.app.services.note_service import NoteService

router = APIRouter()



def get_note_service() -> NoteService:
    return NoteService()

@router.get("/", summary="笔记列表")
async def get_list(
        current_user: User = Depends(get_current_user),
        note_service: NoteService = Depends(get_note_service)
):
  notes = await note_service.get_list(current_user.id)
  return success(data=[NoteResponse.model_validate(note).model_dump() for note in notes])

@router.post('/',summary="新建笔记")
async def create(
        current_user: User = Depends(get_current_user),
        note_service: NoteService = Depends(get_note_service)
):
    note = await note_service.create(current_user.id)
    return success(data=NoteDetailResponse.model_validate(note).model_dump())

@router.get("/{note_uuid}", summary="笔记详情")
async def get_one(
        note_uuid: str,
        current_user: User = Depends(get_current_user),
        note_service: NoteService = Depends(get_note_service),
):
    note = await note_service.get_one(note_uuid,current_user.id)
    return success(data=NoteDetailResponse.model_validate(note).model_dump())

@router.put("/{note_uuid}", summary="更新笔记")
async def update(
        note_uuid: str,
        body: NoteUpdateRequest,
        current_user: User = Depends(get_current_user),
        note_service: NoteService = Depends(get_note_service)
):
    note = await note_service.update(note_uuid,current_user.id,body.content)
    return success(data=NoteDetailResponse.model_validate(note).model_dump())

@router.delete("/{note_uuid}", summary="删除笔记")
async def delete(
        note_uuid: str,
        current_user: User = Depends(get_current_user),
        note_service: NoteService = Depends(get_note_service),
):
    await note_service.delete(note_uuid, current_user.id)
    return success(message="删除成功")