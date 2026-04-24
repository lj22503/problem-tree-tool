"""
Core module — 共享核心逻辑
两套前端（Streamlit / Vercel）都调用这里
"""
from .ai_core import (
    AIBackend,
    ClaudeBackend,
    OpenAIBackend,
    DeepSeekBackend,
    get_available_backends,
    create_backend,
    backend_supports_model,
    _BACKEND_DEFAULT_MODEL,
)
from .prompt_engine import PromptEngine, WaterfallPromptEngine
from .models_core import Message, Stage, ProblemSession
from .session_store import SessionStore

__all__ = [
    "AIBackend",
    "ClaudeBackend",
    "OpenAIBackend",
    "DeepSeekBackend",
    "get_available_backends",
    "create_backend",
    "backend_supports_model",
    "_BACKEND_DEFAULT_MODEL",
    "PromptEngine",
    "WaterfallPromptEngine",
    "Message",
    "Stage",
    "ProblemSession",
    "SessionStore",
]
