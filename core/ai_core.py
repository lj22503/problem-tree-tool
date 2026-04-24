"""
AI 后端 — 核心层
统一封装 Claude / OpenAI / DeepSeek，支持环境变量和 Vercel Secrets
"""

import os
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# 密钥读取工具 — 同时支持 .env 本地开发 和 Vercel Secrets
# ─────────────────────────────────────────────────────────────────────────────
def _get_key(env_name: str, secrets_name: Optional[str] = None) -> Optional[str]:
    """优先从环境变量读取，Vercel 场景也从 os.environ 读（Vercel Secrets 会注入）"""
    key = os.getenv(env_name)
    if key:
        return key
    if secrets_name:
        return os.getenv(secrets_name)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# AIBackend 抽象
# ─────────────────────────────────────────────────────────────────────────────
class AIBackend(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], *, max_tokens: int = 4000,
                 temperature: float = 0.7, model: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def supports_model(self, model_name: str) -> bool:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Claude
# ─────────────────────────────────────────────────────────────────────────────
class ClaudeBackend(AIBackend):
    def __init__(self, api_key: Optional[str] = None):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic 库未安装: pip install anthropic")
        self.api_key = api_key or _get_key("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("未设置 ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, messages: List[Dict[str, str]], *, max_tokens: int = 4000,
                 temperature: float = 0.7, model: Optional[str] = None) -> str:
        model = model or "claude-3-5-sonnet-20241022"
        system = None
        conv = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                conv.append({"role": m["role"], "content": m["content"]})
        resp = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=conv,
        )
        return resp.content[0].text

    def supports_model(self, model_name: str) -> bool:
        return model_name.startswith("claude-")


# ─────────────────────────────────────────────────────────────────────────────
# OpenAI
# ─────────────────────────────────────────────────────────────────────────────
class OpenAIBackend(AIBackend):
    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 库未安装: pip install openai")
        self.api_key = api_key or _get_key("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未设置 OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate(self, messages: List[Dict[str, str]], *, max_tokens: int = 4000,
                 temperature: float = 0.7, model: Optional[str] = None) -> str:
        model = model or "gpt-4o"
        resp = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content

    def supports_model(self, model_name: str) -> bool:
        return model_name.startswith("gpt-") or model_name.startswith("o1")


# ─────────────────────────────────────────────────────────────────────────────
# DeepSeek
# ─────────────────────────────────────────────────────────────────────────────
class DeepSeekBackend(AIBackend):
    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 库未安装（DeepSeek 依赖它）")
        self.api_key = api_key or _get_key("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("未设置 DEEPSEEK_API_KEY")
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )

    def generate(self, messages: List[Dict[str, str]], *, max_tokens: int = 4000,
                 temperature: float = 0.7, model: Optional[str] = None) -> str:
        model = model or "deepseek-chat"
        resp = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content

    def supports_model(self, model_name: str) -> bool:
        return model_name.startswith("deepseek-")


# ─────────────────────────────────────────────────────────────────────────────
# 工厂
# ─────────────────────────────────────────────────────────────────────────────
_BACKEND_CLASSES = {
    "claude": ClaudeBackend,
    "openai": OpenAIBackend,
    "deepseek": DeepSeekBackend,
}

_BACKEND_DEFAULT_MODEL = {
    "claude": "claude-3-5-sonnet-20241022",
    "openai": "gpt-4o",
    "deepseek": "deepseek-chat",
}


def create_backend(backend: str, api_key: Optional[str] = None) -> AIBackend:
    cls = _BACKEND_CLASSES.get(backend)
    if not cls:
        available = list(_BACKEND_CLASSES.keys())
        raise ValueError(f"不支持的后端 '{backend}'，可用: {available}")
    return cls(api_key=api_key)


def get_available_backends() -> List[str]:
    available = []
    if ANTHROPIC_AVAILABLE and _get_key("ANTHROPIC_API_KEY"):
        available.append("claude")
    if OPENAI_AVAILABLE:
        if _get_key("OPENAI_API_KEY"):
            available.append("openai")
        if _get_key("DEEPSEEK_API_KEY"):
            available.append("deepseek")
    return available


def backend_supports_model(backend: str, model_name: str) -> bool:
    cls = _BACKEND_CLASSES.get(backend)
    if not cls:
        return False
    try:
        instance = cls()
        return instance.supports_model(model_name)
    except Exception:
        return False
