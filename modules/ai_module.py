"""
AI集成模块
处理与AI模型的交互，管理提示词系统
"""

import os
import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json

# 尝试导入AI库
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

class AIBackend(ABC):
    """AI后端抽象类"""

    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """生成响应"""
        pass

    @abstractmethod
    def supports_model(self, model_name: str) -> bool:
        """检查是否支持特定模型"""
        pass

class ClaudeBackend(AIBackend):
    """Claude API后端"""

    def __init__(self, api_key: Optional[str] = None):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic库未安装，请运行: pip install anthropic")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("未提供Claude API密钥")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """生成Claude响应"""
        model = kwargs.get("model", "claude-3-5-sonnet-20241022")
        max_tokens = kwargs.get("max_tokens", 4000)
        temperature = kwargs.get("temperature", 0.7)

        # 转换消息格式
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=conversation_messages
        )

        return response.content[0].text

    def supports_model(self, model_name: str) -> bool:
        """检查是否支持Claude模型"""
        # Claude模型通常以"claude-"开头
        return model_name.startswith("claude-")

class OpenAIBackend(AIBackend):
    """OpenAI API后端"""

    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai库未安装，请运行: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未提供OpenAI API密钥")

        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """生成OpenAI响应"""
        model = kwargs.get("model", "gpt-4")
        max_tokens = kwargs.get("max_tokens", 2000)
        temperature = kwargs.get("temperature", 0.7)

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    def supports_model(self, model_name: str) -> bool:
        """检查是否支持OpenAI模型"""
        # OpenAI模型通常以"gpt-"开头，但也可以是其他
        return model_name.startswith("gpt-") or model_name.startswith("o1-") or model_name.startswith("dall-e-")


class DeepSeekBackend(AIBackend):
    """DeepSeek API后端（与OpenAI兼容）"""

    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai库未安装，请运行: pip install openai")

        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("未提供DeepSeek API密钥")

        # DeepSeek使用OpenAI兼容的API，但base_url不同
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """生成DeepSeek响应"""
        model = kwargs.get("model", "deepseek-chat")
        max_tokens = kwargs.get("max_tokens", 2000)
        temperature = kwargs.get("temperature", 0.7)

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    def supports_model(self, model_name: str) -> bool:
        """检查是否支持DeepSeek模型"""
        # DeepSeek模型通常以"deepseek-"开头
        return model_name.startswith("deepseek-")


class PromptEngine:
    """提示词引擎，管理问题树框架的提示词"""

    def __init__(self):
        self.system_prompt = """你是一个名为"灵光问题树"的专家级问题解决教练。你精通"全景式问题解决树"框架，该框架融合了流程推进与思维深度。

你的核心任务：根据用户提出的任何初始问题，引导用户完成一个系统的问题解决流程，最终生成一份结构清晰、可操作、有深度的问题树报告，并支持导出。

你的核心工作流与能力：
1. 主动引导：你不只是被动回答，而是像一个教练一样，按照框架步骤主动提问，引导用户思考。
2. 动态判断：根据用户的回答，判断当前处于哪个步骤，并推进到下一步。如果用户回答浅显，你要用"心智透镜"深挖。
3. 实时可视化：在对话过程中，用清晰的Markdown格式（如列表、表格、加粗标题）动态构建和展示问题树的各个部分，让用户随时看到进展。
4. 生成最终报告：在流程结束时，将所有信息整合成一份完整的、格式优美的报告。
5. 支持导出：报告生成后，明确告知用户可以提供纯文本、Markdown或PDF格式（需说明PDF需用户自行转换）的导出。

你遵循的"全景式问题解决树"框架（七步闭环）：
【流程引擎】
0. 问题淬炼：通过提问，衍生和聚焦真问题。
1. 问题定义：精准结构化定义选定的核心问题。
2. 成功标准：设定清晰、可衡量的解决目标。
3. 挑战评估：识别障碍与风险。
4. 方案生成：创造并选择行动路径。
5. 行动与迭代：规划近期行动并建立复盘机制。

【思维引擎】（全程渗透）
在每一步，你都要自然地运用五大心智透镜引导用户思考：证据、视角、联系、猜想、相关。
并用两大洞察力标准（看得远-回路、看得透-层级）来评估问题的深度。

你的交互风格：
- 温暖而专业：像一位耐心的搭档。
- 多使用提问句："如果……会怎样？""我们如何知道……？""从……角度看呢？"
- 即时反馈与总结：在用户给出重要回答后，简要总结并确认。
- 控制节奏：一次聚焦一个步骤，完成后再推进。如果用户跳跃，礼貌地引导回当前步骤。"""

        self.stage_prompts = {
            "problem_refinement": {
                "name": "问题淬炼",
                "guidance": "在直接寻找解决方案前，我们不妨先花点时间，确保我们正在解决最核心的问题。让我问你几个问题，帮你更清晰地聚焦。",
                "questions": [
                    "（证据）你说'[问题关键词]'，具体是指哪方面？有什么具体的例子吗？",
                    "（视角）如果你的同事或上级来评价这个问题，他们会怎么说？他们的看法和你一致吗？",
                    "（联系）这种感觉，在什么时间、什么情况下最明显？有规律吗？",
                    "（猜想）如果我们不叫它'[问题关键词]'，它可能是什么问题？",
                    "（相关）解决好这个问题，对你来说为什么特别重要？"
                ]
            },
            "problem_definition": {
                "name": "问题定义",
                "guidance": "我们来给这个问题画个清晰的像。请尝试用一句中性的语言描述它，比如'在……情况下，我面临着……挑战，导致了……结果'。"
            },
            "success_criteria": {
                "name": "成功标准",
                "guidance": "想象这个问题已经被完美解决了，你会看到什么现象？感觉到什么？请描述一下那个'胜利的画面'。另外，有哪些可以衡量的指标能证明你成功了？"
            },
            "challenge_assessment": {
                "name": "挑战评估",
                "guidance": "通往这个胜利画面的路上，主要的'路障'可能是什么？可以从内部（如习惯、技能）和外部（如环境、他人）两个方面想想。"
            },
            "solution_generation": {
                "name": "方案生成",
                "guidance": "现在，我们来头脑风暴可能的'过桥'方案。先天马行空，任何想法都可以。然后我们再一起评估和聚焦。"
            },
            "action_iteration": {
                "name": "行动与迭代",
                "guidance": "基于我们选定的方案，第一步可以是什么？下周可以做什么？我们如何建立一个简单的机制，来回顾进展并调整方向？"
            }
        }

    def get_stage_prompt(self, stage: str, problem: str = "") -> str:
        """获取特定阶段的提示词"""
        # 映射Stage枚举值到stage_prompts键
        stage_mapping = {
            "0-问题淬炼": "problem_refinement",
            "1-问题定义": "problem_definition",
            "2-成功标准": "success_criteria",
            "3-挑战评估": "challenge_assessment",
            "4-方案生成": "solution_generation",
            "5-行动与迭代": "action_iteration",
            "已完成": "completed"
        }

        # 如果stage是Stage枚举值，转换为对应的键
        stage_key = stage_mapping.get(stage, stage)

        if stage_key in self.stage_prompts:
            prompt_data = self.stage_prompts[stage_key]
            prompt = f"## 当前阶段: {prompt_data['name']}\n\n{prompt_data['guidance']}"

            if "questions" in prompt_data and problem:
                # 替换问题中的关键词
                questions = []
                for q in prompt_data['questions']:
                    q = q.replace("[问题关键词]", problem[:20])
                    questions.append(q)

                prompt += "\n\n你可以从这些问题开始思考:\n" + "\n".join([f"- {q}" for q in questions])

            return prompt
        else:
            return "让我们继续推进问题解决流程。"

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.system_prompt

class ProblemTreeAI:
    """问题树AI主类"""

    def __init__(self, backend: str = "claude", api_key: Optional[str] = None):
        self.prompt_engine = PromptEngine()
        self.backend_type = backend
        self.api_key = api_key

        # 初始化后端
        if backend == "claude":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic库未安装")
            self.backend = ClaudeBackend(api_key)
        elif backend == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai库未安装")
            self.backend = OpenAIBackend(api_key)
        elif backend == "deepseek":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai库未安装，DeepSeek需要openai库")
            self.backend = DeepSeekBackend(api_key)
        else:
            raise ValueError(f"不支持的AI后端: {backend}")

    def start_session(self, problem: str, model: str = "claude-3-5-sonnet") -> str:
        """开始新会话"""
        system_prompt = self.prompt_engine.get_system_prompt()

        # 初始消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我的问题是: {problem}"},
            {"role": "assistant", "content": self.prompt_engine.get_stage_prompt("problem_refinement", problem)}
        ]

        # 获取AI响应
        response = self.backend.generate_response(
            messages=messages,
            model=model
        )

        return response

    def continue_session(self, messages: List[Dict[str, str]], current_stage: str, model: str = "claude-3-5-sonnet") -> str:
        """继续会话"""
        # 添加系统提示（如果尚未添加）
        if not any(msg["role"] == "system" for msg in messages):
            system_prompt = self.prompt_engine.get_system_prompt()
            messages = [{"role": "system", "content": system_prompt}] + messages

        # 获取当前阶段的提示词
        stage_prompt = self.prompt_engine.get_stage_prompt(current_stage)

        # 在消息中添加当前阶段信息
        # 如果最后一条消息不是系统消息，添加阶段提示
        if messages and messages[-1]["role"] != "system":
            # 添加一条系统消息作为阶段提示
            messages.append({"role": "system", "content": stage_prompt})
        else:
            # 如果最后一条是系统消息，合并阶段信息
            messages[-1]["content"] = messages[-1]["content"] + "\n\n" + stage_prompt

        # 获取AI响应
        response = self.backend.generate_response(
            messages=messages,
            model=model
        )

        return response

    def generate_final_report(self, session_data: Dict[str, Any]) -> str:
        """生成最终报告 - 使用AI基于对话历史生成结构化报告"""
        try:
            # 从会话数据中提取消息
            messages = session_data.get('messages', [])
            problem_statement = session_data.get('problem_statement', '')

            # 准备提示词，让AI基于对话历史生成报告
            report_prompt = f"""请基于以下问题解决对话，生成一份完整的"全景式问题解决树"报告。

原始问题: {problem_statement}

对话历史:
"""
            # 添加对话历史（限制长度）
            for msg in messages[-20:]:  # 只取最近20条消息
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:200]  # 截断长内容
                report_prompt += f"{role}: {content}\n"

            report_prompt += """
请按照以下结构生成报告（使用中文）：

# 问题树分析报告

## 一、原始问题
[简要描述原始问题]

## 二、淬炼后的核心问题
[基于对话提炼的核心问题，总结用户最终聚焦的核心问题]

## 三、问题定义
- **结构化陈述**: [用中性语言结构化描述问题]
- **边界与范围**: [明确问题的边界和讨论范围]
- **关键利益相关方**: [识别关键利益相关方]

## 四、成功标准
- **定性描述（胜利画面）**: [描述问题解决后的理想状态]
- **关键指标（KPIs）**: [可衡量的成功指标]

## 五、关键挑战与风险评估
- **内部障碍**: [内部的主要挑战]
- **外部障碍**: [外部的主要挑战]
- **最高风险项**: [最重要的风险项]

## 六、解决方案与行动计划
- **首选方案**: [推荐的主要解决方案]
- **具体行动步骤**:
  1. （近期）[近期可执行的具体行动]
  2. （中期）[中期行动计划]
- **复盘与调整机制**: [如何跟踪进展和调整方案]

## 七、核心洞察（AI视角）
- **关于"回路"**: [分析此问题可能涉及的增强/调节回路]
- **关于"层级"**: [指出本次分析触及了哪个系统层级]
- **关键心智突破点**: [总结过程中最重要的思维转折]

---
**报告生成时间**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**注意**: 请确保报告内容基于对话历史，避免使用"[...]"等占位符。
"""

            # 使用AI生成报告
            ai_messages = [
                {"role": "system", "content": "你是一个专业的问题解决教练，擅长生成结构化的问题分析报告。"},
                {"role": "user", "content": report_prompt}
            ]

            report = self.backend.generate_response(
                messages=ai_messages,
                model="deepseek-chat" if self.backend_type == "deepseek" else "claude-3-5-sonnet"
            )

            return report

        except Exception as e:
            # 如果AI生成失败，返回基本报告模板
            return f"""# 问题树分析报告

## 一、原始问题
{session_data.get('problem_statement', '')}

## 二、淬炼后的核心问题
[基于对话提炼的核心问题 - 请根据对话历史填写]

## 三、问题定义
- **结构化陈述**: [...]
- **边界与范围**: [...]
- **关键利益相关方**: [...]

## 四、成功标准
- **定性描述（胜利画面）**: [...]
- **关键指标（KPIs）**: [...]

## 五、关键挑战与风险评估
- **内部障碍**: [...]
- **外部障碍**: [...]
- **最高风险项**: [...]

## 六、解决方案与行动计划
- **首选方案**: [...]
- **具体行动步骤**:
  1. （近期）[...]
  2. （中期）[...]
- **复盘与调整机制**: [...]

## 七、核心洞察（AI视角）
- **关于"回路"**: [分析此问题可能涉及的增强/调节回路]
- **关于"层级"**: [指出本次分析触及了哪个系统层级]
- **关键心智突破点**: [总结过程中最重要的思维转折]

---
**报告生成时间**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**导出提示**: 此报告基于对话历史生成。方括号[...]部分需要根据上方对话记录填写具体内容。
**错误信息**: AI报告生成失败: {str(e)}
"""

# 实用函数
def get_available_backends() -> List[str]:
    """获取可用的AI后端"""
    backends = []
    if ANTHROPIC_AVAILABLE:
        backends.append("claude")
    if OPENAI_AVAILABLE:
        backends.append("openai")
        backends.append("deepseek")
    return backends