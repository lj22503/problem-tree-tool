"""
会话存储 — 核心层
Vercel 环境用内存存储（serverless 无持久磁盘）
Streamlit 环境可继续用文件存储（由 utils.py 提供）
"""

import time
import threading
from typing import Dict, Optional

from .models_core import ProblemSession


# ─────────────────────────────────────────────────────────────────────────────
# 内存会话存储（Vercel / Serverless 用）
# ─────────────────────────────────────────────────────────────────────────────
class MemorySessionStore:
    """线程安全的内存会话存储。数据不持久化，每次 cold start 重新开始。"""

    _lock = threading.Lock()
    _sessions: Dict[str, ProblemSession] = {}

    @classmethod
    def save(cls, session: ProblemSession) -> None:
        with cls._lock:
            cls._sessions[session.session_id] = session

    @classmethod
    def get(cls, session_id: str) -> Optional[ProblemSession]:
        with cls._lock:
            return cls._sessions.get(session_id)

    @classmethod
    def list_all(cls) -> Dict[str, ProblemSession]:
        with cls._lock:
            return dict(cls._sessions)

    @classmethod
    def delete(cls, session_id: str) -> bool:
        with cls._lock:
            if session_id in cls._sessions:
                del cls._sessions[session_id]
                return True
            return False

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._sessions.clear()


# 兼容性别名
SessionStore = MemorySessionStore
