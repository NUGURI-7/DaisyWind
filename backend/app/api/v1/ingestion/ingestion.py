from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.core.depends import get_current_user
from backend.app.core.response import success, error
from backend.app.ingestion.schemas import Blackboard
from backend.app.models import User
from backend.app.models.ingestion_model import WorkflowTemplate, IngestionRun
from backend.app.ingestion.graph.engine import GraphEngine
from backend.app.schemas.ingestion_schema import IngestionRequest

router = APIRouter()


@router.post("/run", summary="启动 Ingestion 工作流")
async def run_ingestion(
        request: IngestionRequest,
        current_user: User = Depends(get_current_user)
):
    # 查找最新版本的 workflow template
    template = await WorkflowTemplate.filter(
        workflow_key=request.workflow_key
    ).order_by("-version").first()
    if not template:
        return error(code=404, message=f"工作流 {request.workflow_key} 不存在")

    run = await IngestionRun.create(
        user=current_user,
        template=template,
        source_type=request.source_type,
        source_ref=request.source_ref,
        graph_snapshot=template.definition,
        blackboard=Blackboard(
            source_type=request.source_type,
            source_ref=request.source_ref,
            source_input=request.source_input,
            paste_format=request.paste_format,
        ).model_dump()
    )

    engine = GraphEngine(run)
    await engine.run_to_completion()
    result = Blackboard.model_validate(run.blackboard)
    return success(data={
        "run_uuid": str(run.uuid),
        "status": run.status,
        "note_uuid": result.note_uuid,
        "draft": result.draft or "",
        "outline": result.outline,  # {"title": "...", "tags": [...], "summary": "..."}
    })
