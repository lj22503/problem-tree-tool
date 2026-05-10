"""
提示词引擎 — 核心层
对话模式 + 瀑布模式，两套提示词系统
"""

from typing import Dict, Any, Optional


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


class IterativeWaterfallEngine:
    """
    迭代深化版瀑布引擎。

    工作流程：
    1. Scanner（第1轮）→ 快速扫描，产出骨架 + 标记未知点
    2. 收敛判断 → AI 自检是否有显著未知点
    3. 若未收敛 → DeepDiver（第2、3、...轮）→ 针对未知点深挖
    4. 收敛后 → FinalIntegration → 输出完整报告

    最大迭代轮次由 max_rounds 控制（默认3轮即停止，防止无限循环）。
    """

    MAX_ROUNDS = 3  # 安全阀：最多迭代3轮深挖

    def __init__(self):
        self.system_prompt = ITERATIVE_WATERFALL_SYSTEM

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def build_scanner_prompt(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx_str = ""
        if context:
            ctx_str = "\n".join(f"- **{k}**: {v}" for k, v in context.items())
        return SCANNER_TEMPLATE.format(
            question=question,
            context=ctx_str or "无"
        )

    def build_convergence_judge_prompt(
        self,
        question: str,
        current_round_content: str,
        round_num: int,
        history: str = ""
    ) -> str:
        return CONVERGENCE_JUDGE_TEMPLATE.format(
            question=question,
            analysis=current_round_content,
            round_num=round_num,
            history=history or "（首轮无历史记录）"
        )

    def build_deepdiver_prompt(
        self,
        question: str,
        existing_analysis: str,
        unknown_points: str,
        round_num: int
    ) -> str:
        return DEEPDIVER_TEMPLATE.format(
            question=question,
            existing_analysis=existing_analysis,
            unknown_points=unknown_points,
            round_num=round_num
        )

    def build_final_integration_prompt(
        self,
        question: str,
        all_rounds: str
    ) -> str:
        return FINAL_INTEGRATION_TEMPLATE.format(
            question=question,
            all_rounds=all_rounds
        )

    def run(
        self,
        question: str,
        backend,  # AIBackend 实例
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 6000,
        progress_callback=None  # 可选：每轮结束后回调，用于 Streamlit 进度更新
    ) -> str:
        """
        执行迭代深化流程。

        Args:
            question: 用户问题
            backend: AIBackend 实例（如 ClaudeBackend）
            context: 额外上下文
            max_tokens: 每次生成的 max_tokens
            progress_callback: fn(round_num, stage, content) 进度回调

        Returns:
            最终整合报告字符串
        """
        rounds = []  # 记录每轮的分析内容

        # ── 第1轮：Scanner ──────────────────────────────────────────────
        scanner_prompt = self.build_scanner_prompt(question, context)

        if progress_callback:
            progress_callback(0, "scanning", "")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": scanner_prompt}
        ]
        scanner_result = backend.generate_response(messages, max_tokens=max_tokens)
        rounds.append({"stage": "scanner", "content": scanner_result})

        if progress_callback:
            progress_callback(1, "scanner_done", scanner_result)

        # ── 收敛判断（第1轮后）─────────────────────────────────────────
        judge_prompt = self.build_convergence_judge_prompt(
            question=question,
            current_round_content=scanner_result,
            round_num=1,
            history=""
        )
        judge_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": judge_prompt}
        ]
        judge_result = backend.generate_response(judge_messages, max_tokens=500)
        converged = "已收敛" in judge_result and "未收敛" not in judge_result

        if progress_callback:
            progress_callback(1, "judge", judge_result)

        # ── 第2、3轮：DeepDiver（若需要）────────────────────────────────
        round_num = 2
        while not converged and round_num <= self.MAX_ROUNDS:
            # 从判断结果中提取下一个要深挖的点
            # judge_result 里最后一行应该是 "如果未收敛，明确说出下一个最需要深挖的点是什么：..."
            unknown_points = self._extract_unknown_points(judge_result)

            if not unknown_points.strip():
                # 提取失败，默认使用 scanner_result 中的模糊点描述
                unknown_points = "基于上一轮分析，选择最关键的一个模糊点进行深挖。"

            deepdiver_prompt = self.build_deepdiver_prompt(
                question=question,
                existing_analysis=scanner_result + "\n\n---\n\n历史轮次：\n" + "\n\n---\n\n".join(
                    f"【第{r['stage']}】" + r["content"] for r in rounds
                ),
                unknown_points=unknown_points,
                round_num=round_num
            )

            if progress_callback:
                progress_callback(round_num, "deepdiving", "")

            deepdiver_messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": deepdiver_prompt}
            ]
            deepdiver_result = backend.generate_response(deepdiver_messages, max_tokens=max_tokens)
            rounds.append({"stage": f"deepdiver_r{round_num}", "content": deepdiver_result})

            if progress_callback:
                progress_callback(round_num, "deepdiver_done", deepdiver_result)

            # 再次收敛判断
            history_str = "\n\n".join(
                f"【第{round_num}轮 - {r['stage']}】\n{r['content']}"
                for round_num, r in enumerate(rounds, 1)
            )
            judge_prompt_2 = self.build_convergence_judge_prompt(
                question=question,
                current_round_content=deepdiver_result,
                round_num=round_num,
                history=history_str
            )
            judge_messages_2 = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": judge_prompt_2}
            ]
            judge_result_2 = backend.generate_response(judge_messages_2, max_tokens=500)
            converged = "已收敛" in judge_result_2 and "未收敛" not in judge_result_2

            if progress_callback:
                progress_callback(round_num, "judge", judge_result_2)

            round_num += 1

        # ── 最终整合 ──────────────────────────────────────────────────────
        if progress_callback:
            progress_callback(round_num - 1, "integrating", "")

        all_rounds_str = "\n\n".join(
            f"=== 【第{round_num}轮 - {r['stage']}】 ===\n{r['content']}"
            for round_num, r in enumerate(rounds, 1)
        )
        integration_prompt = self.build_final_integration_prompt(
            question=question,
            all_rounds=all_rounds_str
        )
        integration_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": integration_prompt}
        ]
        final_report = backend.generate_response(integration_messages, max_tokens=max_tokens)

        if progress_callback:
            progress_callback(round_num - 1, "done", final_report)

        return final_report

    def _extract_unknown_points(self, judge_result: str) -> str:
        """从收敛判断结果中提取下一个要深挖的点。"""
        lines = judge_result.strip().split("\n")
        # 找包含"下一个最需要深挖"或"如果未收敛"那一行
        for i, line in enumerate(lines):
            if "下一个最需要深挖" in line or ("未收敛" in line and "点" in line):
                # 收集后面几行作为 unknown_points
                return "\n".join(lines[i:]).strip()
        # 回退：返回 judge_result 最后 200 字
        return judge_result[-500:].strip()
