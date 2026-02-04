"""
    @project: Windify
    @Author: niu
    @file: user.py
    @date: 2026/2/3 20:49
    @desc:
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    pass