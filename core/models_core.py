"""
数据模型 — 核心层
"""

import datetime
import json
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class Stage(Enum):
    """问题解决阶段"""
    PROBLEM_REFINEMENT = "0-问题淬炼"
    PROBLEM_DEFINITION = "1-问题定义"
    SUCCESS_CRITERIA = "2-成功标准"
    CHALLENGE_ASSESSMENT = "3-挑战评估"
    SOLUTION_GENERATION = "4-方案生成"
    ACTION_ITERATION = "5-行动与迭代"
    COMPLETED = "已完成"


STAGE_DISPLAY = {
    "0-问题淬炼": "问题淬炼",
    "1-问题定义": "问题定义",
    "2-成功标准": "成功标准",
    "3-挑战评估": "挑战评估",
    "4-方案生成": "方案生成",
    "5-行动与迭代": "行动与迭代",
    "已完成": "已完成",
}

STAGES_ORDERED = [
    Stage.PROBLEM_REFINEMENT,
    Stage.PROBLEM_DEFINITION,
    Stage.SUCCESS_CRITERIA,
    Stage.CHALLENGE_ASSESSMENT,
    Stage.SOLUTION_GENERATION,
    Stage.ACTION_ITERATION,
    Stage.COMPLETED,
]


@dataclass
class Message:
    role: str       # "user" | "assistant" | "system"
    content: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class ProblemSession:
    """会话"""
    problem_statement: str
    session_name: str = ""
    ai_model: str = "deepseek-chat"
    backend: str = "deepseek"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    messages: List[Message] = field(default_factory=list)
    current_stage: Stage = Stage.PROBLEM_REFINEMENT
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def __post_init__(self):
        if not self.session_name:
            self.session_name = self.problem_statement[:30] + "..."

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
        self.updated_at = datetime.datetime.now()

    def advance_stage(self) -> None:
        """推进到下一阶段"""
        idx = STAGES_ORDERED.index(self.current_stage)
        if idx < len(STAGES_ORDERED) - 1:
            self.current_stage = STAGES_ORDERED[idx + 1]
        self.updated_at = datetime.datetime.now()

    def is_complete(self) -> bool:
        return self.current_stage == Stage.COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "problem_statement": self.problem_statement,
            "session_name": self.session_name,
            "ai_model": self.ai_model,
            "backend": self.backend,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [m.to_dict() for m in self.messages],
            "current_stage": self.current_stage.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProblemSession":
        session = cls(
            problem_statement=data["problem_statement"],
            session_name=data.get("session_name", ""),
            ai_model=data.get("ai_model", "deepseek-chat"),
            backend=data.get("backend", "deepseek"),
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.datetime.fromisoformat(data["updated_at"]),
            session_id=data["session_id"],
        )
        session.messages = [Message.from_dict(m) for m in data.get("messages", [])]
        session.current_stage = Stage(data["current_stage"])
        return session
