from __future__ import annotations
from typing import Any

from pydantic import BaseModel, Field, model_validator


class NodeSpec(BaseModel):
    id: str                 # 节点唯一 id，如 "classifier"
    type: str               # 节点类型，如 "classifier"，必须在注册表里存在
    params: dict[str,Any] = Field(default_factory=dict) # 节点私有参数



class EdgeSpec(BaseModel):
    id: str                                    # 边的 id，如 "e3"
    source: str                                # 起点节点 id
    target: str                                # 终点节点 id
    condition: str | None = None               # 条件分支用，如 "pass" / "fail"
    back_edge: bool = False                    # 是否回环边
    max_iterations: int | None = None          # 回环最大次数（back_edge=True 时必填）

    @model_validator(mode="after")
    def _validate_back_edge(self) -> EdgeSpec:
        if self.back_edge:
            if self.max_iterations is None or self.max_iterations <= 0:
                raise ValueError(
                    f"边 {self.id}: back_edge=True 时 max_iterations 必须为正整数"
                )
        return self


class WorkflowSpec(BaseModel):
    """整张工作流的定义，对应一份 YAML 文件。"""
    key: str                                   # workflow_key
    version: int                               # 单调递增
    description: str = ""
    schema_version: int = 1                    # 引擎能识别的图 schema 版本
    nodes: list[NodeSpec]
    edges: list[EdgeSpec]

    @model_validator(mode="after")
    def _validate_topology(self) -> WorkflowSpec:
        """校验拓扑"""
        node_ids = [n.id for n in self.nodes]
        if node_ids.__len__() != set(node_ids).__len__():
            raise ValueError(f"工作流 {self.key} 节点 id 存在重复")

        edge_ids = [e.id for e in self.edges]
        if edge_ids.__len__() != set(edge_ids).__len__():
            raise ValueError(f"工作流 {self.key} 边 id 存在重复")

        node_id_set = set(node_ids)
        for edge in self.edges:
            if edge.source not in node_id_set:
                raise ValueError(f"边 {edge.id}: source 节点 {edge.source} 不存在")
            if edge.target not in node_id_set:
                raise ValueError(f"边 {edge.id}: target 节点 {edge.target} 不存在")

        targets_set = {e.target for e in self.edges}
        entries = [n for n in self.nodes if n.id not in targets_set]

        if entries.__len__() != 1:
            raise ValueError(
                f"工作流 {self.key} 必须有恰好一个入口节点（无入边的节点），"
                f"当前找到 {len(entries)} 个: {[n.id for n in entries]}"
            )
        return self

    def _find_entry_node(self) -> NodeSpec:
        targets_set = {e.target for e in self.edges}
        for node in self.nodes:
            if node.id not in targets_set:
                return node
        raise RuntimeError("入口节点未找到，理论上不会发生（已被 _validate_topology 拦截）")

    def to_db_definition(self) -> dict[str,Any]:
        """转成 workflow_template.definition 字段的 JSONB 内容。"""
        return {
            "schema_version": self.schema_version,
            "entry_node": self._find_entry_node().id,
            "nodes": [n.model_dump() for n in self.nodes],
            "edges": [e.model_dump(exclude_none=True) for e in self.edges]
        }


