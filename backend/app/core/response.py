"""
统一响应格式
"""
from typing import TypeVar, Generic, Optional, List, Any

from pydantic import BaseModel

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PageData(BaseModel, Generic[T]):
    total: int
    records: List[T]
    current_page: int
    page_size: int


def success(data: Any = None, message: str = "success") -> dict:
    """
    成功响应
    :param data: 响应数据
    :param message: 提示信息
    """
    return {
        "code": 200,
        "message": message,
        "data": data
    }

def error(message: str = "Error", code: int = 500, data: Any = None) -> dict:
    """
    失败响应
    :param message: 错误信息
    :param code: 错误代码
    :param data: 额外数据
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }

def page(total: int, records: list, current_page: int = 1, page_size: int = 10) -> dict:
    """
    分页响应
    :param total: 总数
    :param records: 记录列表
    :param current_page: 当前页
    :param page_size: 每页大小
    """
    return {
        "code": 200,
        "message": "Success",
        "data": {
            "total": total,
            "records": records,
            "current_page": current_page,
            "page_size": page_size
        }
    }

