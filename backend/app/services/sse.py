"""
    @project: DaisyWind
    @Author: niu
    @file: sse.py
    @date: 2026/4/12 14:43
    @desc: SSE 事件构造工具
"""

import json
from typing import Any






def sse_event(event: str, data: Any = None) -> str:
    """构造一个 SSE 事件字符串。

    Args:
        event: 事件类型，如 "message_start", "content_block_delta"
        data: 任意可序列化数据，会被 json.dumps

    Returns:
        格式化的 SSE 文本，末尾含空行分隔符
    """
    payload = json.dumps(data, ensure_ascii=False) if data is not None else "{}"
    return f"event: {event}\ndata: {payload}\n\n"
