"""
Unit tests for GapDrivenEngine and YouxianMapEngine
No real API calls - all tests use mock objects
"""

import pytest
from core.gap_engine import JudgeResult, GapDrivenEngine
from core.prompt_engine import YouxianMapEngine, IterativeWaterfallEngine


# =============================================================================
# JudgeResult Tests
# =============================================================================

def test_from_json_valid_converged():
    json_str = '{"verdict": "CONVERGED", "next_gaps": [], "reason": "done", "knowledge_summary": "all good"}'
    result = JudgeResult.from_json_str(json_str)
    assert result.verdict == "CONVERGED"
    assert result.next_gaps == []


def test_from_json_valid_continue():
    json_str = '{"verdict": "CONTINUE", "next_gaps": ["gap1", "gap2"], "reason": "more needed", "knowledge_summary": ""}'
    result = JudgeResult.from_json_str(json_str)
    assert result.verdict == "CONTINUE"
    assert len(result.next_gaps) == 2


def test_from_json_missing_keys_defaults():
    result = JudgeResult.from_json_str('{"verdict": "CONVERGED"}')
    assert result.verdict == "CONVERGED"
    assert result.next_gaps == []  # default
    assert result.reason == ""     # default


def test_from_json_broken_falls_back_to_converged():
    result = JudgeResult.from_json_str("CONVERGED yes this is done")
    assert result.verdict == "CONVERGED"


def test_from_json_broken_falls_back_to_continue():
    result = JudgeResult.from_json_str("some unclear output")
    assert result.verdict == "CONTINUE"


# =============================================================================
# GapDrivenEngine / YouxianMapEngine Instance Tests (no API calls)
# =============================================================================

def test_engine_init():
    engine = YouxianMapEngine()
    assert engine.gap_queue == []
    assert engine.knowledge == []
    assert engine.diary == []
    assert engine._round == 0


def test_engine_alias():
    """IterativeWaterfallEngine is an alias for YouxianMapEngine"""
    assert IterativeWaterfallEngine is YouxianMapEngine


def test_engine_has_required_methods():
    engine = YouxianMapEngine()
    assert hasattr(engine, "_scan")
    assert hasattr(engine, "_judge")
    assert hasattr(engine, "_deepdive")
    assert hasattr(engine, "_integrate")
    assert hasattr(engine, "run")


def test_gap_queue_pop():
    engine = YouxianMapEngine()
    engine.gap_queue = ["gap1", "gap2"]
    popped = engine.gap_queue.pop(0)
    assert popped == "gap1"
    assert engine.gap_queue == ["gap2"]


def test_knowledge_accumulation():
    engine = YouxianMapEngine()
    engine.knowledge.append({"round": 0, "stage": "scanner", "gap": "init", "answer": "skeleton"})
    engine.knowledge.append({"round": 1, "stage": "deepdiver", "gap": "risk", "answer": "analysis"})
    assert len(engine.knowledge) == 2
    assert engine.knowledge[1]["gap"] == "risk"


def test_complexity_assessment_mock():
    """Mock backend returning '复杂' should give max_rounds=5"""
    engine = YouxianMapEngine()

    class MockBackend:
        def generate_response(self, messages, max_tokens=200):
            return "复杂"

    max_rounds = engine._assess_complexity("test question", MockBackend())
    assert max_rounds == 5


def test_complexity_assessment_simple():
    """Mock backend returning '简单' should give max_rounds=1"""
    engine = YouxianMapEngine()

    class MockBackend:
        def generate_response(self, messages, max_tokens=200):
            return "简单"

    max_rounds = engine._assess_complexity("test question", MockBackend())
    assert max_rounds == 1


def test_complexity_assessment_default():
    """Mock backend returning unknown should give max_rounds=3 (default)"""
    engine = YouxianMapEngine()

    class MockBackend:
        def generate_response(self, messages, max_tokens=200):
            return "unknown"

    max_rounds = engine._assess_complexity("test question", MockBackend())
    assert max_rounds == 3  # default


def test_summarize_knowledge_under_limit():
    """Knowledge under MAX_KNOWLEDGE limit should show all items"""
    engine = YouxianMapEngine()
    engine.knowledge = [{"gap": "g1", "answer": "a1"}, {"gap": "g2", "answer": "a2"}]
    summary = engine._summarize_knowledge()
    assert "g1" in summary
    assert "g2" in summary


def test_summarize_knowledge_over_limit():
    """Knowledge over MAX_KNOWLEDGE limit should include compression notice"""
    engine = YouxianMapEngine()
    # MAX_KNOWLEDGE = 10, add 12 items
    engine.knowledge = [{"gap": f"g{i}", "answer": f"a{i}"} for i in range(12)]
    summary = engine._summarize_knowledge()
    assert "仅展示最近结果" in summary  # compression notice
    # last items should be visible
    assert "g11" in summary
    # early items may be dropped
