"""
    @project: DaisyWind
    @file: sync.py
    @desc: 启动时把 templates/*.yaml 同步到 workflow_template 表。
           - 完全一致：跳过
           - 同 (key, version) 但内容不同：报错
           - 新版本：INSERT
"""


import logging
from pathlib import Path
from typing import Any

import yaml

from backend.app.ingestion.nodes import registry
from backend.app.ingestion.graph.schema import WorkflowSpec
from backend.app.models import WorkflowTemplate

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

class WorkflowSyncConflictError(Exception):
    """同 (workflow_key, version) 已存在但内容不一致。"""


def _parse_yaml_file(path: Path) -> WorkflowSpec:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        raise ValueError(f"{path} 顶层必须是 mapping")
    return WorkflowSpec.model_validate(raw)

def _validate_against_registry(spec: WorkflowSpec) -> None:
    """校验 spec 里每个节点的 type 都在注册表里，每个节点的 params 符合该类型的 Params 模型。"""
    for node in spec.nodes:
        try:
            node_cls = registry.get(node.type)
        except KeyError:
            raise ValueError(
                f"工作流 {spec.key} 节点 {node.id} 的 type={node.type!r} 未注册"
            )

        try:
            node_cls.Params.model_validate(node.params)
        except Exception as e:
            raise ValueError(
                f"工作流 {spec.key} 节点 {node.id} 的 params 校验失败: {e}"
            )

async def _sync_one(spec: WorkflowSpec, source_path: str) -> None:
    _validate_against_registry(spec)

    new_definition: dict[str, Any] = spec.to_db_definition()

    existing = await WorkflowTemplate.get_or_none(
        workflow_key=spec.key, version=spec.version
    )
    if existing is not None:
        if existing.definition == new_definition:
            logger.info(
                "workflow %s v%d 已同步且内容一致，跳过", spec.key, spec.version
            )
            return
        raise WorkflowSyncConflictError(
            f"workflow {spec.key} v{spec.version} 已存在但内容不一致；"
            f"请 bump version 而不是修改已有版本"
        )

    parent_version = (
        await WorkflowTemplate.filter(workflow_key=spec.key)
        .order_by("-version")
        .first()
    )
    await WorkflowTemplate.create(
        workflow_key=spec.key,
        version=spec.version,
        parent_version=parent_version,
        definition=new_definition,
        source_path=source_path,
        is_system=True
    )
    logger.info(
        "workflow %s v%d 已同步入库（parent=%s）",
        spec.key,
        spec.version,
        parent_version,
    )

async def sync_workflow_templates() -> None:
    """扫描 templates/*.yaml 全部同步入库。FastAPI lifespan 启动时调用。"""
    if not TEMPLATES_DIR.is_dir():
        logger.warning("templates 目录不存在：%s", TEMPLATES_DIR)
        return
    yaml_files = sorted(TEMPLATES_DIR.glob("*.yaml"))
    if not yaml_files:
        logger.info("templates 目录无 yaml 文件，跳过同步")
        return

    for yaml_file in yaml_files:
        spec = _parse_yaml_file(yaml_file)
        await _sync_one(spec, source_path=yaml_file.name)


