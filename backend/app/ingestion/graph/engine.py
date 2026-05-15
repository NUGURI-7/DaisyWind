"""
    @project: DaisyWind
    @file: engine.py
    @desc: 图执行引擎：加载快照 → 找 ready 节点 → 执行 → 推进。
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from backend.app.ingestion.nodes import registry
from backend.app.ingestion.graph.schema import NodeSpec
from backend.app.ingestion.nodes.base import NodeContext
from backend.app.ingestion.schemas import Blackboard
from backend.app.models.ingestion_model import IngestionRun, IngestionEvent


logger = logging.getLogger(__name__)

# 节点状态常量
PENDING = "pending"
RUNNING = "running"
DONE = "done"
FAILED = "failed"

class GraphEngine:
    """从 IngestionRun 加载图快照，驱动节点依次执行。"""

    def __init__(self, run: IngestionRun):
        self._run = run
        self._snapshot: dict[str, Any] = run.graph_snapshot
        raw = dict(run.blackboard or {})
        node_status = raw.pop("__node_status__",{})
        self._blackboard = Blackboard.model_validate(raw)
        self._node_status: dict[str,str] = node_status

        for node_spec in self._snapshot.get("nodes",[]):
            if node_spec["id"] not in self._node_status:
                self._node_status[node_spec["id"]] = PENDING

    def find_ready_nodes(self) -> list[NodeSpec]:
        """找所有 pending 且前置节点全部 done 的节点。"""
        edges = self._snapshot.get("edges",[])
        ready: list[NodeSpec] = []

        for node_dict in self._snapshot.get("nodes",[]):
            node_id = node_dict["id"]
            if self._node_status.get(node_id) != PENDING:
                continue
            # 前任节点
            predecessors = [
                e["source"] for e in edges if e["target"] == node_id
            ]

            if all( self._node_status.get(p) == DONE for p in predecessors):
                ready.append(NodeSpec.model_validate(node_dict))

        return ready

    async def _emit(self, event_type: str, actor: str, payload: dict[str, Any]) -> None:
        """记录事件到 IngestionEvent 表。seq 由 DB 原子自增保证唯一。"""
        from tortoise.transactions import in_transaction

        async with in_transaction() as conn:
            rows = await conn.execute_query_dict(
                "UPDATE ingestion_run SET last_event_seq = last_event_seq + 1 "
                "WHERE id = $1 RETURNING last_event_seq",
                [self._run.id],
            )
            seq = rows[0]["last_event_seq"]
            await IngestionEvent.create(
                run_id=self._run.id,
                seq=seq,
                actor=actor,
                kind=event_type,
                payload=payload,
                using_db=conn
            )

    async def persist(self):
        """ blackboard + node_status 持久化到 DB。"""
        snapshot = self._blackboard.model_dump()
        snapshot["__node_status__"] = self._node_status
        self._run.blackboard = snapshot
        await self._run.save(update_fields=["blackboard", "status", "updated_at"])

    async def run_to_completion(self):
        """主循环：反复找 ready → 执行 → 更新状态，直到没有 ready 节点。"""

        self._run.status = "running"
        await self._run.save(update_fields=["status"])

        while True:
            ready = self.find_ready_nodes()
            if not ready:
                break

            for node_spec in ready:
                self._node_status[node_spec.id] = RUNNING
                await self.persist()

                try:
                    patch = await self.execute_node(node_spec)
                    self._blackboard = self._blackboard.model_copy(update=patch)
                    self._node_status[node_spec.id] = DONE
                except Exception as e:
                    self._node_status[node_spec.id] = FAILED
                    self._run.status = "failed"
                    await self.persist()
                    logger.exception("节点 %s 执行失败", node_spec.id)
                    raise
        self._run.status = "succeeded"
        await self.persist()
        logger.info("run %s 执行完成", self._run.uuid)

    async def execute_node(self, node_spec: NodeSpec) -> dict[str,Any]:
        """实例化节点并执行，返回 patch。"""
        node_cls = registry.get(node_spec.type)
        node = node_cls()
        params = node_cls.Params.model_validate(node_spec.params)

        ctx = NodeContext(
            run_id=self._run.id,
            user_id=self._run.user_id,
            blackboard=self._blackboard,
            cancel_token=asyncio.Event(),
            emit=self._emit,
        )
        await self._emit("node_started", node_spec.id, {"type": node_spec.type})
        logger.info("执行节点 %s (type=%s)", node_spec.id, node_spec.type)
        patch = await node.run(ctx,params)
        logger.info("节点 %s 执行完成，patch keys: %s", node_spec.id, list(patch.keys()))
        await self._emit("node_completed", node_spec.id, {"type": node_spec.type, "patch_keys": list(patch.keys())})
        return patch



















