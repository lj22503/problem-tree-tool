"""
提示词引擎 — 核心层
对话模式 + 瀑布模式，两套提示词系统
"""

from typing import Dict, Any, Optional
from core.gap_engine import GapDrivenEngine, JudgeResult


# ─────────────────────────────────────────────────────────────────────────────
# 对话模式 System Prompt
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """你是一个名为"灵光问题树"的专家级问题解决教练，精通"全景式问题解决树"框架。

你的核心任务：根据用户提出的任何初始问题，引导用户完成系统的问题解决流程（七步闭环），最终生成结构清晰、可操作的问题树报告。

你的核心工作流与能力：
1. 主动引导：像一个教练一样，按照框架步骤主动提问，引导用户思考。
2. 动态判断：根据用户的回答，判断当前处于哪个步骤，并推进到下一步。
3. 实时可视化：用清晰的Markdown格式（列表、表格、加粗标题）动态构建问题树。
4. 生成最终报告：流程结束时，将所有信息整合成完整报告。

你遵循的"全景式问题解决树"框架（七步闭环）：
0. 问题淬炼：通过提问，衍生和聚焦真问题。
1. 问题定义：精准结构化定义选定的核心问题。
2. 成功标准：设定清晰、可衡量的解决目标。
3. 挑战评估：识别障碍与风险。
4. 方案生成：创造并选择行动路径。
5. 行动与迭代：规划近期行动并建立复盘机制。

【思维引擎】（全程渗透）
在每一步，自然地运用五大心智透镜引导用户思考：
- 证据透镜：区分事实与假设
- 视角透镜：从多利益相关方角度审视
- 联系透镜：识别问题之间的关联
- 猜想透镜：提出大胆假设，挑战默认前提
- 相关透镜：区分重要与紧急

交互风格：
- 温暖而专业：像一位耐心的搭档
- 多使用提问句：多问"如果……会怎样？""我们如何知道……？"
- 即时反馈与总结：用户给出重要回答后，简要总结并确认
- 控制节奏：一次聚焦一个步骤，完成后再推进"""


STAGE_PROMPTS: Dict[str, Dict[str, str]] = {
    "0-问题淬炼": {
        "name": "问题淬炼",
        "guidance": "在寻找解决方案之前，让我们先花点时间，确保我们正在解决最核心的问题。",
        "questions": [
            "（证据）你说'[问题关键词]'，具体是指哪方面？有什么具体的例子吗？",
            "（视角）如果你的同事或上级来评价这个问题，他们会怎么说？",
            "（联系）这种感觉，在什么时间、什么情况下最明显？有规律吗？",
            "（猜想）如果我们不叫它'[问题关键词]'，它可能是什么问题？",
            "（相关）解决好这个问题，对你来说为什么特别重要？",
        ],
    },
    "1-问题定义": {
        "name": "问题定义",
        "guidance": "我们来给这个问题画个清晰的像。请尝试用一句中性的语言描述它，比如'在……情况下，我面临着……挑战，导致了……结果'。",
        "questions": [],
    },
    "2-成功标准": {
        "name": "成功标准",
        "guidance": "想象这个问题已经被完美解决了，你会看到什么现象？感觉到什么？请描述一下那个'胜利的画面'。另外，有哪些可以衡量的指标能证明你成功了？",
        "questions": [],
    },
    "3-挑战评估": {
        "name": "挑战评估",
        "guidance": "通往这个胜利画面的路上，主要的'路障'可能是什么？可以从内部（如习惯、技能）和外部（如环境、他人）两个方面想想。",
        "questions": [],
    },
    "4-方案生成": {
        "name": "方案生成",
        "guidance": "现在，我们来头脑风暴可能的'过桥'方案。先天马行空，任何想法都可以。然后我们再一起评估和聚焦。",
        "questions": [],
    },
    "5-行动与迭代": {
        "name": "行动与迭代",
        "guidance": "基于我们选定的方案，第一步可以是什么？下周可以做什么？我们如何建立一个简单的机制，来回顾进展并调整方向？",
        "questions": [],
    },
    "已完成": {
        "name": "已完成",
        "guidance": "🎉 问题树构建完成！以下是你的完整分析报告。",
        "questions": [],
    },
}


STAGE_MAPPING: Dict[str, str] = {
    "0-问题淬炼": "0-问题淬炼",
    "1-问题定义": "1-问题定义",
    "2-成功标准": "2-成功标准",
    "3-挑战评估": "3-挑战评估",
    "4-方案生成": "4-方案生成",
    "5-行动与迭代": "5-行动与迭代",
    "已完成": "已完成",
}


# ─────────────────────────────────────────────────────────────────────────────
# PromptEngine — 对话模式
# ─────────────────────────────────────────────────────────────────────────────
class PromptEngine:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.stage_prompts = STAGE_PROMPTS

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def get_stage_prompt(self, stage_value: str, problem: str = "") -> str:
        stage_key = STAGE_MAPPING.get(stage_value, stage_value)
        data = self.stage_prompts.get(stage_key)
        if not data:
            return "让我们继续推进问题解决流程。"

        prompt = f"## 当前阶段: {data['name']}\n\n{data['guidance']}"

        if data["questions"] and problem:
            qs = [q.replace("[问题关键词]", problem[:20]) for q in data["questions"]]
            prompt += "\n\n你可以从这些问题开始思考:\n" + "\n".join(f"- {q}" for q in qs)

        return prompt


# ─────────────────────────────────────────────────────────────────────────────
# WaterfallPromptEngine — 瀑布模式
# ─────────────────────────────────────────────────────────────────────────────
WATERFALL_SYSTEM_PROMPT = """你是一位资深的系统性问题分析专家。
你的任务是使用「思维树构建师」框架，对用户的问题进行一次性完整分析。

输出格式必须严格按照以下结构，使用 Markdown 排版："""

WATERFALL_TEMPLATE = """# 思维树构建师

## 结构化问题分析

### 🎯 核心问题提炼
用户的核心问题是：
[重述用户问题]

表面看是 [表面问题]，但本质是：
[本质洞察]

### 📋 问题范围界定
问题聚焦于'[问题领域]'：

关键要素：
1. [要素 1]
2. [要素 2]
3. [要素 3]

### 🏆 成功目标设定
成功意味着：

可衡量标准：
1. [可衡量指标 1]
2. [可衡量指标 2]

### ⚠️ 风险挑战识别
主要挑战：
1. [挑战 1]：
2. [挑战 2]：

### 💡 解决方案制定
首选方案：
[推荐方案描述]

具体行动步骤：
1. （近期）[行动]
2. （中期）[行动]

### 🔄 行动计划
第一步：[立即可做的事]
复盘节点：[何时回顾]

## 多维度思维分析

### 🔍 事实依据
[分析问题所需的关键事实]

### 👁️ 多维视角
[从不同利益相关方角度的分析]

### 🔗 关联分析
[问题之间的联系和反馈回路]

### 🧠 合理推论
[基于证据的推断]

### 📊 重要性评估
[评估各要素的重要程度]

[额外上下文]
"""


class WaterfallPromptEngine:
    def __init__(self):
        self.system_prompt = WATERFALL_SYSTEM_PROMPT

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def build_prompt(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        prompt = WATERFALL_TEMPLATE.replace("[重述用户问题]", question)
        if context:
            ctx_str = "\n".join(f"- **{k}**: {v}" for k, v in context.items())
            prompt = prompt.replace("[额外上下文]", f"\n\n## 额外上下文\n{ctx_str}")
        return prompt


# ─────────────────────────────────────────────────────────────────────────────
# 迭代深化版瀑布引擎 — DeepResearch 风格
# AI 自主判断迭代深度，收敛即停止
# ─────────────────────────────────────────────────────────────────────────────

ITERATIVE_WATERFALL_SYSTEM = """你是一位资深的问题分析专家。

你的独特之处在于：**你会先扫描问题骨架，明确知道什么是你确定的，什么是需要深挖的**，然后再深入研究。

不是一次把所有东西都堆出来，而是有层次地展开。
"""

# 第1轮：扫描 — 快速产出骨架 + 标记未知点
SCANNER_TEMPLATE = """## 任务：快速扫描，建立分析骨架

**用户问题**：
{question}

**额外上下文**：
{context}

## 你的输出要求

请先用「思维树构建师」框架对这个问题的整体维度进行**快速扫描**（不要深挖每个点），然后在最后明确列出：

### 已清晰的事实与推断
[列出3-5个你有信心的事实/推断，用一句话概括一个]

### 存在的模糊点或未验证假设
[列出2-4个你不确定、需要深挖的点，每个点用一句话说明为什么不确定]

**原则**：
- 扫描要快，框架要全，不要在一个点上停留太久
- 模糊点要诚实，这是下一步深挖的材料
- 结构要清晰，让你自己（和用户）一眼看出哪些是"有根有据"，哪些是"待验证"
"""

# 收敛判断 prompt
CONVERGENCE_JUDGE_TEMPLATE = """## 任务：收敛判断

你是你自己。你刚刚完成了第 {round_num} 轮分析。

**用户原始问题**：{question}

**本轮分析内容**：
{analysis}

**你的分析深度记录**（之前各轮结论摘要）：
{history}

## 判断标准

满足以下任一条件，判定为「已收敛」：
1. 核心问题定义清晰，解决方案具体可操作
2. 所有关键模糊点都已被论证或明确标注为"开放问题"
3. 再多一轮迭代，边际收益极低（信息已饱和）

满足以下条件，判定为「未收敛」：
1. 存在2个以上关键模糊点仍未被论证
2. 解决方案还停留在"方向性"而非"可操作性"
3. 你明确感觉到还有重要因素没被覆盖

## 输出格式

请直接回答：
**收敛判断**：已收敛 / 未收敛

**理由**（1-3句话）：
**如果未收敛，明确说出下一个最需要深挖的点是什么**（用一句话）：
"""

# 后续轮：深挖 — 针对模糊点一个个深挖
DEEPDIVER_TEMPLATE = """## 任务：深挖第 {round_num} 轮

**用户原始问题**：
{question}

**已有分析**：
{existing_analysis}

**本轮要深挖的模糊点**：
{unknown_points}

## 你的任务

从以上模糊点中，选择**最关键的一个**进行深度分析。

深度分析要求：
1. 收集或推理支撑这个点的具体事实/数据/逻辑链
2. 给出明确的结论（即使是"证据不足，暂定假设X"）
3. 指出这个点分析完之后，是否还有残留问题

**注意**：一次只深挖一个点，但要挖透。不要展开其他框架部分。
"""

# 最终整合
FINAL_INTEGRATION_TEMPLATE = """## 任务：整合最终报告

**用户原始问题**：
{question}

**所有迭代轮次的分析**：
{all_rounds}

## 输出要求

请把所有轮次的分析整合为一份完整的「思维树构建师」报告。

整合原则：
- 合并重复内容，保留最深入的那个版本
- 模糊点已被论证的，使用论证结论
- 仍无法论证的，明确标注为「开放考量」
- 确保从问题到方案形成完整闭环

输出格式：标准的「思维树构建师」Markdown 报告（与框架模板一致）
"""


# ─────────────────────────────────────────────────────────────────────────────
# YouxianMapEngine — 游刃 Map 实现，继承 GapDrivenEngine
# ─────────────────────────────────────────────────────────────────────────────

class YouxianMapEngine(GapDrivenEngine):
    """
    游刃 Map 问题树引擎。
    继承 GapDrivenEngine 通用骨架，注入游刃专属 prompt 模板。
    """

    _SYSTEM_PROMPT = ITERATIVE_WATERFALL_SYSTEM

    _SCANNER_TEMPLATE = SCANNER_TEMPLATE  # 复用现有模板

    _JUDGE_TEMPLATE = """## 任务：收敛判断 + 生成候选深挖点

你是你自己。你刚刚完成了第 {round_num} 轮分析。

**用户原始问题**：{question}

**本轮分析内容**：
{current_analysis}

**已有知识积累**：
{knowledge_summary}

**gap 队列**：{gap_queue}

## 判断标准

满足以下任一条件，判定为「已收敛」：
1. 核心问题定义清晰，解决方案具体可操作
2. 所有关键模糊点都已被论证或明确标注为"开放问题"
3. 再多一轮迭代，边际收益极低

## 输出格式（JSON，必须包含 verdict, next_gaps, reason, knowledge_summary）

```json
{{
  "verdict": "CONVERGED" | "CONTINUE",
  "next_gaps": ["gap1", "gap2"] 或 [],
  "reason": "判断理由（1-3句话）",
  "knowledge_summary": "当前知识总结（200字以内）"
}}
```"""

    _DEEPDIVER_TEMPLATE = DEEPDIVER_TEMPLATE  # 复用现有模板

    _INTEGRATION_TEMPLATE = FINAL_INTEGRATION_TEMPLATE  # 复用现有模板

    def _scan(
        self,
        question: str,
        context: Optional[Dict[str, Any]],
        backend,
        max_tokens: int,
    ) -> str:
        ctx_str = ""
        if context:
            ctx_str = "\n".join(f"- **{k}**: {v}" for k, v in context.items())
        prompt = self._SCANNER_TEMPLATE.format(
            question=question,
            context=ctx_str or "无",
        )
        messages = [
            {"role": "system", "content": self._SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return backend.generate_response(messages, max_tokens=max_tokens)

    def _judge(self, question: str, backend, max_tokens: int) -> JudgeResult:
        knowledge_summary = self._summarize_knowledge()
        gap_queue_str = "\n".join(f"- {g}" for g in self.gap_queue) if self.gap_queue else "（空）"

        # 获取当前轮次的分析内容（最后一条 knowledge）
        current_analysis = self.knowledge[-1]["answer"] if self.knowledge else ""

        prompt = self._JUDGE_TEMPLATE.format(
            question=question,
            round_num=self._round,
            current_analysis=current_analysis,
            knowledge_summary=knowledge_summary,
            gap_queue=gap_queue_str,
        )
        messages = [
            {"role": "system", "content": self._SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        result = backend.generate_response(messages, max_tokens=max_tokens)
        return JudgeResult.from_json_str(result)

    def _deepdive(
        self,
        question: str,
        current_gap: str,
        backend,
        max_tokens: int,
    ) -> str:
        existing = self._format_knowledge()
        prompt = self._DEEPDIVER_TEMPLATE.format(
            question=question,
            existing_analysis=existing,
            unknown_points=current_gap,
            round_num=self._round,
        )
        messages = [
            {"role": "system", "content": self._SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return backend.generate_response(messages, max_tokens=max_tokens)

    def _integrate(self, question: str, backend, max_tokens: int) -> str:
        all_rounds = "\n\n".join(
            f"=== 【第{k['round']}轮 - {k['stage']}】===\n{k['answer']}"
            for k in self.knowledge
        )
        prompt = self._INTEGRATION_TEMPLATE.format(
            question=question,
            all_rounds=all_rounds,
        )
        messages = [
            {"role": "system", "content": self._SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return backend.generate_response(messages, max_tokens=max_tokens)


# ─────────────────────────────────────────────────────────────────────────────
# 兼容性别名
# ─────────────────────────────────────────────────────────────────────────────
IterativeWaterfallEngine = YouxianMapEngine
