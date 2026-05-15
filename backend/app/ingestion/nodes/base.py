"""
    @project: DaisyWind
    @file: base.py
    @desc: 节点类型抽象基类与节点运行时上下文。
"""

from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Any, Awaitable, ClassVar

from pydantic import BaseModel

from backend.app.ingestion.schemas import Blackboard

EmitFn = Callable[[str,str, dict[str,Any]], Awaitable[None]]


@dataclass
class NodeContext:
    """引擎在调度节点前构造并传入的运行时上下文。"""
    run_id: int
    user_id: int
    blackboard: Blackboard
    cancel_token: asyncio.Event
    emit: EmitFn


class NodeType(ABC):
    """所有节点类型的抽象基类。子类必须覆盖类属性并实现 run。"""

    type_name: ClassVar[str]
    display_name: ClassVar[str]
    description: ClassVar[str]
    Params: ClassVar[type[BaseModel]]
    inputs: ClassVar[list[str]]
    outputs: ClassVar[list[str]]
    idempotent: ClassVar[bool] = False # 是否幂等

    @abstractmethod
    async def run(self, ctx: NodeContext, params: BaseModel) -> dict[str, Any]:
        """执行节点，返回要合并进 blackboard 的 patch。
                节点不应直接修改 ctx.blackboard；失败请抛异常，由引擎捕获标记 failed。
                """