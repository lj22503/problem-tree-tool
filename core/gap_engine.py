"""
GapDrivenEngine — 通用迭代深化骨架
抽象基类 + 子类注入 prompt 模板，复杂度自适应轮次
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable


# ─────────────────────────────────────────────────────────────────────────────
# JudgeResult — 结构化收敛判断返回值
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class JudgeResult:
    """Judge 层结构化返回值"""
    verdict: str           # "CONVERGED" | "CONTINUE"
    next_gaps: List[str]  # 2-3 个候选 gap（CONVERGED 时为空）
    reason: str           # 判断理由，1-3 句话
    knowledge_summary: str # 当前知识总结（用于日志）

    @classmethod
    def from_json_str(cls, json_str: str) -> "JudgeResult":
        """从 JSON 字符串解析，兼容格式错误的响应"""
        try:
            data = json.loads(json_str)
            return cls(
                verdict=data.get("verdict", "CONTINUE"),
                next_gaps=data.get("next_gaps", []),
                reason=data.get("reason", ""),
                knowledge_summary=data.get("knowledge_summary", ""),
            )
        except (json.JSONDecodeError, KeyError):
            # 降级：如果 JSON 解析失败，尝试从纯文本推断
            text = json_str.upper()
            if "CONVERGED" in text and "CONTINUE" not in text:
                return cls(verdict="CONVERGED", next_gaps=[], reason=json_str[-200:], knowledge_summary="")
            return cls(verdict="CONTINUE", next_gaps=[], reason=json_str[-200:], knowledge_summary="")


# ─────────────────────────────────────────────────────────────────────────────
# GapDrivenEngine — 抽象基类
# ─────────────────────────────────────────────────────────────────────────────
class GapDrivenEngine(ABC):
    """
    通用迭代深化骨架。

    子类注入：
    - _SYSTEM_PROMPT, _SCANNER_TEMPLATE, _JUDGE_TEMPLATE,
      _DEEPDIVER_TEMPLATE, _INTEGRATION_TEMPLATE
    - _COMPLEXITY_TEMPLATE（可选，覆盖默认复杂度评估）

    工作流程：
    1. 复杂度评估（_assess_complexity）→ max_rounds
    2. Scanner（_scan）→ 骨架 + 初始 gaps
    3. 循环直到 CONVERGED 或 max_rounds：
         Judge → 判断收敛 / 返回 next_gaps
         DeepDiver → 深挖当前 gap
    4. Integration → 最终报告
    """

    # ── 子类必须注入 ──────────────────────────────────────────────────────────
    _SYSTEM_PROMPT: str = ""
    _SCANNER_TEMPLATE: str = ""
    _JUDGE_TEMPLATE: str = ""
    _DEEPDIVER_TEMPLATE: str = ""
    _INTEGRATION_TEMPLATE: str = ""

    # ── 可选覆盖 ──────────────────────────────────────────────────────────────
    _COMPLEXITY_TEMPLATE: str = """## 任务：快速评估问题复杂度

问题：{question}

请快速判断这个问题需要多深的分析，直接输出：

- 简单：max_rounds=1（事实型/单维度问题）
- 中等：max_rounds=2-3（多维度/有模糊点）
- 复杂：max_rounds=4-5（跨领域/开放判断）

直接输出等级词，不要解释。"""

    # ── 固定参数 ──────────────────────────────────────────────────────────────
    MAX_KNOWLEDGE: int = 10   # 知识积累上限，超限后 judge 使用压缩摘要
    MAX_ROUNDS: int = 5      # 迭代轮次上限

    def __init__(self):
        self.gap_queue: List[str] = []
        self.knowledge: List[Dict[str, Any]] = []
        self.diary: List[str] = []
        self._round: int = 0

    # ── 子类可覆盖 ────────────────────────────────────────────────────────────

    def _assess_complexity(self, question: str, backend) -> int:
        """评估问题复杂度，返回 max_rounds。子类可覆盖 _COMPLEXITY_TEMPLATE。"""
        prompt = self._COMPLEXITY_TEMPLATE.format(question=question)
        messages = [
            {"role": "system", "content": self._SYSTEM_PROMPT or "你是一个问题分析专家。"},
            {"role": "user", "content": prompt},
        ]
        result = backend.generate_response(messages, max_tokens=200)
        result_upper = result.upper().strip()

        if "简单" in result_upper or "max_rounds=1" in result_upper:
            return 1
        elif "复杂" in result_upper or "max_rounds=4" in result_upper or "max_rounds=5" in result_upper:
            return 5
        return 3  # 默认中等

    def _summarize_knowledge(self) -> str:
        """知识超限时生成压缩摘要"""
        if len(self.knowledge) <= self.MAX_KNOWLEDGE:
            return self._format_knowledge()
        # 截断，只保留最近 N 条
        recent = self.knowledge[-self.MAX_KNOWLEDGE:]
        return "（知识积累较多，仅展示最近结果）\n" + self._format_knowledge_list(recent)

    def _format_knowledge(self) -> str:
        return self._format_knowledge_list(self.knowledge)

    def _format_knowledge_list(self, items: List[Dict[str, Any]]) -> str:
        if not items:
            return "暂无"
        lines = []
        for i, k in enumerate(items, 1):
            lines.append(f"{i}. 【{k.get('gap', 'unknown')}】{k.get('answer', '')[:300]}")
        return "\n".join(lines)

    def _parse_scanner_output(self, scanner_result: str) -> Dict[str, Any]:
        """从 scanner 输出中提取骨架和 gaps"""
        gaps = []
        lines = scanner_result.split("\n")
        capture_gaps = False
        for line in lines:
            if "模糊点" in line or "未验证" in line or "gap" in line.lower():
                capture_gaps = True
                continue
            if capture_gaps and line.strip() and (line.startswith("-") or line.startswith("*") or line[0].isdigit()):
                gap = line.lstrip("-*0123456789.、) ").strip()
                if gap:
                    gaps.append(gap)
        # 回退：如果没找到，返回 scanner 最后 500 字作为 gap
        if not gaps:
            gaps = [scanner_result[-500:].strip()]
        return {
            "skeleton": scanner_result,
            "gaps": gaps,
        }

    # ── 核心迭代 ──────────────────────────────────────────────────────────────

    def run(
        self,
        question: str,
        backend,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 6000,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        主循环。

        Args:
            question: 用户问题
            backend: AIBackend 实例
            context: 额外上下文
            max_tokens: 每次生成的最大 token 数
            progress_callback: fn(round_num, stage, content) 进度回调

        Returns:
            最终整合报告字符串
        """
        self.gap_queue = []
        self.knowledge = []
        self.diary = []
        self._round = 0

        # ── 第0步：复杂度评估 ──────────────────────────────────────────────
        if progress_callback:
            progress_callback(0, "assessing_complexity", "")
        max_rounds = self._assess_complexity(question, backend)

        # ── 第1步：Scanner ─────────────────────────────────────────────────
        if progress_callback:
            progress_callback(0, "scanning", "")
        scanner_result = self._scan(question, context, backend, max_tokens)
        parsed = self._parse_scanner_output(scanner_result)
        self.gap_queue = parsed["gaps"]
        self.knowledge.append({
            "round": 0,
            "stage": "scanner",
            "gap": "初始骨架",
            "answer": parsed["skeleton"],
        })
        self.diary.append(f"第0轮 Scanner：识别 {len(self.gap_queue)} 个初始 gaps")

        if progress_callback:
            progress_callback(0, "scanner_done", scanner_result)

        # ── 迭代主循环 ─────────────────────────────────────────────────────
        self._round = 1
        while self._round <= max_rounds:
            # Judge
            judge_result = self._judge(question, backend, max_tokens=500)
            if progress_callback:
                progress_callback(self._round, "judge", str(judge_result))

            if judge_result.verdict == "CONVERGED":
                self.diary.append(f"第{self._round}轮 Judge：已收敛，停止迭代")
                break

            # 取下一个 gap
            if not judge_result.next_gaps:
                # 没有返回 gap，用队列中剩余的
                if self.gap_queue:
                    current_gap = self.gap_queue.pop(0)
                else:
                    break  # 没有 gap 可挖
            else:
                current_gap = judge_result.next_gaps[0]
                # 保留其他候选 gaps 到队列
                remaining = [g for g in judge_result.next_gaps[1:] if g not in self.gap_queue]
                self.gap_queue = remaining + self.gap_queue

            # DeepDiver
            if progress_callback:
                progress_callback(self._round, "deepdiving", current_gap)
            dive_result = self._deepdive(question, current_gap, backend, max_tokens)

            self.knowledge.append({
                "round": self._round,
                "stage": "deepdiver",
                "gap": current_gap,
                "answer": dive_result,
            })
            self.diary.append(f"第{self._round}轮 DeepDiver：深挖「{current_gap[:30]}...」")

            if progress_callback:
                progress_callback(self._round, "deepdiver_done", dive_result)

            self._round += 1

        # ── 最终整合 ───────────────────────────────────────────────────────
        if progress_callback:
            progress_callback(self._round, "integrating", "")
        final_report = self._integrate(question, backend, max_tokens)
        if progress_callback:
            progress_callback(self._round, "done", final_report)
        return final_report

    # ── 子类必须实现 ─────────────────────────────────────────────────────────

    @abstractmethod
    def _scan(
        self,
        question: str,
        context: Optional[Dict[str, Any]],
        backend,
        max_tokens: int,
    ) -> str:
        """Scanner：快速扫描，产出骨架 + 初始 gaps"""
        pass

    @abstractmethod
    def _judge(self, question: str, backend, max_tokens: int) -> JudgeResult:
        """Judge：判断收敛，返回结构化 JudgeResult"""
        pass

    @abstractmethod
    def _deepdive(
        self,
        question: str,
        current_gap: str,
        backend,
        max_tokens: int,
    ) -> str:
        """DeepDiver：深挖单个 gap"""
        pass

    @abstractmethod
    def _integrate(self, question: str, backend, max_tokens: int) -> str:
        """Integration：整合所有知识，输出最终报告"""
        pass
