"""
    @project: DaisyWind
    @file: __init__.py
    @desc: 导入此包即触发所有节点类型注册到 registry。
"""
from backend.app.ingestion.nodes import sink_node  # noqa: F401

__all__ = ["sink_node"]