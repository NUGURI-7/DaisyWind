"""
    @project: DaisyWind
    @Author: niu
    @file: media.py.py
    @date: 2026/3/12 09:59
    @desc: 媒体资源相关接口
"""
import uuid
from fastapi import APIRouter, Depends, UploadFile, File

from pydantic import BaseModel
from backend.app.core.depends import get_current_user
from backend.app.core.exceptions import AppApiException
from backend.app.core.response import success
from backend.app.core.storage import r2_storage
from backend.app.models import User
from config import settings

router = APIRouter()

class PresignRequest(BaseModel):
    filename: str
    content_type: str = "application/octet-stream"


@router.post("/presigned-url", summary="获取对象存储直传预签名URL")
async def get_presigened_url(
    req: PresignRequest,
    current_user: User = Depends(get_current_user)
):
    """
    给前端颁发一个限时 5 分钟的上传令牌（直传 URL）
    后端完全不接触文件流
    """
    # 提取后缀名
    if '.' not in req.filename:
        raise AppApiException(400, message="上传的文件必须包含有效的扩展名")

    ext = req.filename.split('.')[-1].lower()

    object_name = f"notes/uploads/{uuid.uuid4().hex}.{ext}"

    result = r2_storage.generate_pre_signed_upload_url(
        object_name=object_name,
        content_type=req.content_type
    )

    return success(data={
        "upload_url": result["upload_url"],
        "public_url": result["public_url"],
        "object_name": object_name
    })






