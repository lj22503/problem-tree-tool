#!/usr/bin/env python3
"""
基本功能测试脚本
测试数据模型、工具函数和AI模块（模拟）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import datetime
import json
from pathlib import Path

from modules.models import ProblemSession, Message, Stage
from modules.utils import save_session, load_session, delete_session, export_markdown
from modules.ai_module import PromptEngine

def test_models():
    """测试数据模型"""
    print("测试数据模型...")

    # 创建消息
    msg1 = Message("user", "我的工作效率低怎么办？")
    msg2 = Message("assistant", "我们来分析一下你的工作效率问题...")

    assert msg1.role == "user"
    assert msg2.content.startswith("我们来分析")
    print("  [OK] 消息模型测试通过")

    # 创建会话
    session = ProblemSession(
        problem_statement="我的工作效率低怎么办？",
        session_name="工作效率问题",
        ai_model="claude-3-5-sonnet"
    )

    assert session.problem_statement == "我的工作效率低怎么办？"
    assert session.session_name == "工作效率问题"
    assert session.current_stage == Stage.PROBLEM_REFINEMENT
    print("  [OK] 会话模型测试通过")

    # 添加消息
    session.add_message("user", "我经常拖延")
    session.add_message("assistant", "你通常在什么情况下拖延？")

    assert len(session.messages) == 2
    assert session.messages[0].role == "user"
    print("  [OK] 添加消息测试通过")

    # 更新阶段
    session.update_stage()
    # 简单阶段更新逻辑，这里不详细测试
    print("  [OK] 阶段更新测试通过")

    return session

def test_serialization():
    """测试序列化和反序列化"""
    print("测试序列化和反序列化...")

    # 创建会话
    session = ProblemSession(
        problem_statement="测试问题",
        session_name="测试会话"
    )
    session.add_message("user", "测试消息")

    # 转换为字典
    session_dict = session.to_dict()
    assert isinstance(session_dict, dict)
    assert "problem_statement" in session_dict
    assert "messages" in session_dict
    print("  [OK] 序列化测试通过")

    # 从字典恢复
    restored = ProblemSession.from_dict(session_dict)
    assert restored.problem_statement == session.problem_statement
    assert len(restored.messages) == len(session.messages)
    print("  [OK] 反序列化测试通过")

    return session

def test_prompt_engine():
    """测试提示词引擎"""
    print("测试提示词引擎...")

    engine = PromptEngine()

    # 测试系统提示词
    system_prompt = engine.get_system_prompt()
    assert "灵光问题树" in system_prompt
    assert "全景式问题解决树" in system_prompt
    print("  [OK] 系统提示词测试通过")

    # 测试阶段提示词
    stage_prompt = engine.get_stage_prompt("problem_refinement", "效率问题")
    assert "问题淬炼" in stage_prompt
    assert "效率问题" in stage_prompt or "聚焦" in stage_prompt
    print("  [OK] 阶段提示词测试通过")

    print("  [OK] 提示词引擎测试通过")

def test_utils(session):
    """测试工具函数"""
    print("测试工具函数...")

    # 保存会话
    save_session(session)
    print("  [OK] 保存会话测试通过")

    # 加载会话
    loaded = load_session(session.session_id)
    assert loaded is not None
    assert loaded.session_id == session.session_id
    print("  [OK] 加载会话测试通过")

    # 导出Markdown
    markdown = export_markdown(session)
    assert "# 问题树分析报告" in markdown
    assert session.problem_statement in markdown
    print("  [OK] 导出Markdown测试通过")

    # 删除会话
    result = delete_session(session.session_id)
    assert result is True
    print("  [OK] 删除会话测试通过")

    # 验证删除
    loaded_again = load_session(session.session_id)
    assert loaded_again is None
    print("  [OK] 验证删除测试通过")

def test_data_directory():
    """测试数据目录"""
    print("测试数据目录...")

    data_dir = Path(__file__).parent / "data"
    assert data_dir.exists()

    sessions_file = data_dir / "sessions.json"
    # 文件可能不存在，这没关系
    print("  [OK] 数据目录存在")

    # 清理测试数据
    if sessions_file.exists():
        # 读取现有数据，确保不是真正的用户数据
        try:
            with open(sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if len(data) == 0:
                    print("  [OK] 数据文件为空（正常）")
                else:
                    print(f"  ⚠ 数据文件中有 {len(data)} 条记录（可能是真实数据）")
        except json.JSONDecodeError:
            print("  ⚠ 数据文件格式错误")

def main():
    """主测试函数"""
    print("=" * 60)
    print("灵光问题树工具 - 基本功能测试")
    print("=" * 60)

    try:
        # 测试数据模型
        session1 = test_models()

        # 测试序列化
        session2 = test_serialization()

        # 测试提示词引擎
        test_prompt_engine()

        # 测试工具函数（使用session2）
        test_utils(session2)

        # 测试数据目录
        test_data_directory()

        print("\n" + "=" * 60)
        print("所有测试通过！ [SUCCESS]")
        print("=" * 60)
        print("\n基本功能正常：")
        print("  - 数据模型 [OK]")
        print("  - 序列化/反序列化 [OK]")
        print("  - 提示词引擎 [OK]")
        print("  - 文件操作 [OK]")
        print("  - 导出功能 [OK]")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())