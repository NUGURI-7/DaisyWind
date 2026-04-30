"""
    @project: DaisyWind
    @file: registry.py
    @desc: 节点类型注册表，所有 NodeType 子类通过 register 报到。
"""

from __future__ import annotations

from backend.app.ingestion.nodes.base import NodeType

_REGISTRY: dict[str, type[NodeType]] = {}


def register(node_cls: type[NodeType]) -> type[NodeType]:
    """注册节点类型。可作为装饰器使用。"""
    if not hasattr(node_cls, "type_name") or not isinstance(node_cls.type_name, str):
        raise ValueError(f"{node_cls.__name__} 必须声明字符串类属性 type_name")
    if not hasattr(node_cls, "Params"):
        raise ValueError(f"{node_cls.__name__} 必须声明 Params 类属性")

    type_name = node_cls.type_name
    if type_name in _REGISTRY:
        existing = _REGISTRY[type_name].__name__
        raise ValueError(
            f"type_name={type_name!r} 已被 {existing} 注册，"
            f"不能再注册 {node_cls.__name__}"
        )

    _REGISTRY[type_name] = node_cls
    return node_cls

def get(type_name: str) -> type[NodeType]:
    """按 type_name 取节点类，未注册抛 KeyError。"""
    if type_name not in _REGISTRY:
        raise KeyError(f"未注册的节点类型: {type_name!r}")
    return _REGISTRY[type_name]

def list_type_names() -> list[str]:
    """列出所有已注册的节点类型名，按字母序。"""
    return sorted(_REGISTRY.keys())










