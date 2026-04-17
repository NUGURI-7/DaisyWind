"""
    @project: DaisyWind
    @Author: niu
    @file: deps.py.py
    @date: 2026/4/10 16:02
    @desc:
"""
from dataclasses import dataclass

from backend.app.models import User, Conversation


@dataclass
class AgentDeps:

    user: User
    conversation: Conversation
