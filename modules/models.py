"""
数据模型定义
"""

import json
import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
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

@dataclass
class Message:
    """对话消息"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"])
        )

@dataclass
class ProblemSession:
    """问题树会话"""
    problem_statement: str
    session_name: str = ""
    ai_model: str = "claude-3-5-sonnet"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    messages: List[Message] = field(default_factory=list)
    current_stage: Stage = Stage.PROBLEM_REFINEMENT
    session_id: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    def __post_init__(self):
        if not self.session_name:
            self.session_name = self.problem_statement[:30] + "..."

    def add_message(self, role: str, content: str):
        """添加消息"""
        self.messages.append(Message(role, content))
        self.updated_at = datetime.datetime.now()

    def update_stage(self):
        """根据对话内容更新阶段（简化逻辑）"""
        # 这里可以实现更智能的阶段判断
        stages = list(Stage)
        current_index = stages.index(self.current_stage)
        if current_index < len(stages) - 1:
            # 改进逻辑：每个阶段需要至少2条消息才能推进
            # 这样可以更快完成流程，同时保持一定深度
            messages_per_stage = 2
            if len(self.messages) >= (current_index + 1) * messages_per_stage:
                self.current_stage = stages[current_index + 1]
        self.updated_at = datetime.datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于JSON序列化"""
        return {
            "session_id": self.session_id,
            "problem_statement": self.problem_statement,
            "session_name": self.session_name,
            "ai_model": self.ai_model,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages],
            "current_stage": self.current_stage.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProblemSession":
        """从字典创建实例"""
        session = cls(
            problem_statement=data["problem_statement"],
            session_name=data["session_name"],
            ai_model=data["ai_model"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.datetime.fromisoformat(data["updated_at"]),
            session_id=data["session_id"]
        )
        session.messages = [Message.from_dict(msg) for msg in data["messages"]]
        session.current_stage = Stage(data["current_stage"])
        return session

    def get_stage_progress(self) -> float:
        """获取阶段进度（0-1）"""
        stages = list(Stage)
        current_index = stages.index(self.current_stage)
        return current_index / (len(stages) - 1)