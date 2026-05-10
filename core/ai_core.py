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
                 temperature: float = 0.7, model: Optional[str] = None,
                 api_key: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def supports_model(self, model_name: str) -> bool:
        pass

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Wrapper: delegates to generate(). Added for interface compatibility with modules/ai_module.py"""
        return self.generate(messages, **kwargs)


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
                 temperature: float = 0.7, model: Optional[str] = None,
                 api_key: Optional[str] = None) -> str:
        model = model or "gpt-4o"
        effective_key = api_key or self.api_key
        client = openai.OpenAI(api_key=effective_key)
        resp = client.chat.completions.create(
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
                 temperature: float = 0.7, model: Optional[str] = None,
                 api_key: Optional[str] = None) -> str:
        model = model or "deepseek-chat"
        effective_key = api_key or self.api_key
        client = openai.OpenAI(api_key=effective_key, base_url="https://api.deepseek.com")
        resp = client.chat.completions.create(
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


# ─────────────────────────────────────────────────────────────────────────────
# 收敛判断 — 对话阶段迭代深化
# ─────────────────────────────────────────────────────────────────────────────
JUDGE_SYSTEM_PROMPT = """你是一个严格的质量审查员。你的任务是对AI在一个问题解决阶段产出的回复进行质量评估，判断其是否足够深入、具体、可操作。

评分标准（0-10分）：
- 6分以下：回复过于笼统、抽象，缺乏具体细节或可操作性，需要继续深挖
- 6-8分：有基础内容，但可以更深入、更具体
- 8分以上：内容扎实，具体、可操作，无需继续

判断标准（输出一个词）：
- "CONVERGED"（收敛）：回复已经足够深入具体，主题明确，无需再深挖
- "DIVERGE"（发散）：回复过于发散，没有聚焦核心问题
- "SUPERFICIAL"（浅薄）：回复有方向但缺乏深度，需要具体化
- "INCOMPLETE"（残缺）：回复有明显遗漏，重要维度没有覆盖
- "GOOD"（良好）：有实质内容但还有深挖空间，可以继续"""


JUDGE_USER_TEMPLATE = """阶段：{stage_name}
阶段指导：{stage_guidance}
AI 回复：
---
{response}
---

请评估：这个回复是否足够深入？如果要继续深挖，你建议从哪个方向切入？"""


class ConvergenceJudge:
    def __init__(self):
        self.system_prompt = JUDGE_SYSTEM_PROMPT

    def build_judge_messages(self, stage_name: str, stage_guidance: str, response: str):
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": JUDGE_USER_TEMPLATE.format(
                stage_name=stage_name,
                stage_guidance=stage_guidance,
                response=response,
            )},
        ]

    def parse_judgment(self, output: str) -> str:
        output = output.strip().upper()
        for keyword in ["CONVERGED", "DIVERGE", "SUPERFICIAL", "INCOMPLETE", "GOOD"]:
            if keyword in output:
                return keyword
        return "GOOD"  # 默认认为良好

    def should_continue(self, output: str) -> bool:
        verdict = self.parse_judgment(output)
        # CONVERGED = 停止，其他 = 继续
        return verdict != "CONVERGED"

    def get_deepdive_prompt(self, stage_name: str, stage_guidance: str, response: str) -> str:
        return f"""你刚才在「{stage_name}」阶段的回复如下：

---
{response}
---

请针对这个回复中的【薄弱环节】进行深入分析。
薄弱环节可能是：
- 过于笼统的描述（需要具体例子）
- 缺乏可操作性的建议（需要具体步骤）
- 遗漏的重要维度（需要补充）
- 表象描述（需要挖掘根本原因）

请输出一段更深入的分析或追问，补充或深化原回复。"""


def backend_supports_model(backend: str, model_name: str) -> bool:
    cls = _BACKEND_CLASSES.get(backend)
    if not cls:
        return False
    try:
        instance = cls()
        return instance.supports_model(model_name)
    except Exception:
        return False
