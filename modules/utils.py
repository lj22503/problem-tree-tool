"""
工具函数
"""

import json
import os
import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import ProblemSession

# 数据存储路径
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SESSIONS_FILE = DATA_DIR / "sessions.json"

def save_session(session: ProblemSession) -> None:
    """保存会话到文件"""
    # 读取现有会话
    sessions = load_all_sessions()

    # 更新或添加会话
    session_dict = session.to_dict()
    session_id = session.session_id

    # 查找现有会话索引
    found = False
    for i, s in enumerate(sessions):
        if s["session_id"] == session_id:
            sessions[i] = session_dict
            found = True
            break

    if not found:
        sessions.append(session_dict)

    # 保存到文件
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

def load_session(session_id: str) -> Optional[ProblemSession]:
    """根据ID加载会话"""
    sessions = load_all_sessions()
    for session_data in sessions:
        if session_data["session_id"] == session_id:
            return ProblemSession.from_dict(session_data)
    return None

def load_all_sessions() -> List[Dict[str, Any]]:
    """加载所有会话"""
    if not SESSIONS_FILE.exists():
        return []

    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            sessions = json.load(f)
            if isinstance(sessions, list):
                return sessions
            else:
                return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def list_sessions() -> List[ProblemSession]:
    """列出所有会话对象"""
    sessions_data = load_all_sessions()
    sessions = []
    for data in sessions_data:
        try:
            session = ProblemSession.from_dict(data)
            sessions.append(session)
        except Exception as e:
            print(f"加载会话时出错: {e}")
            continue
    return sessions

def delete_session(session_id: str) -> bool:
    """删除会话"""
    sessions = load_all_sessions()
    new_sessions = [s for s in sessions if s["session_id"] != session_id]

    if len(new_sessions) == len(sessions):
        return False  # 未找到会话

    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_sessions, f, ensure_ascii=False, indent=2)

    return True

def export_markdown(session: ProblemSession) -> str:
    """导出会话为Markdown报告（基于全景式问题解决树框架）"""

    # 尝试从对话中提取关键信息（简单启发式）
    def extract_key_info(messages):
        """从消息中提取关键信息"""
        user_messages = [msg.content for msg in messages if msg.role == "user"]
        assistant_messages = [msg.content for msg in messages if msg.role == "assistant"]

        # 简单提取：最后几条用户消息可能包含重要信息
        recent_user = user_messages[-3:] if len(user_messages) > 3 else user_messages
        recent_assistant = assistant_messages[-3:] if len(assistant_messages) > 3 else assistant_messages

        return {
            "user_inputs": recent_user,
            "ai_guidance": recent_assistant
        }

    key_info = extract_key_info(session.messages)

    # 按照用户提供的模板生成报告
    report = f"""# 问题树分析报告

## 一、原始问题
{session.problem_statement}

## 二、淬炼后的核心问题
[基于对话提炼的核心问题 - 请根据以下对话内容填写]

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

## 八、完整对话记录

"""

    # 添加对话记录
    for i, msg in enumerate(session.messages):
        role_emoji = {
            "user": "👤 用户",
            "assistant": "🤖 AI教练",
            "system": "⚙️ 系统"
        }.get(msg.role, "📝")

        report += f"### {role_emoji} ({msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')})\n\n"
        report += f"{msg.content}\n\n"
        report += "---\n\n"

    # 添加元数据
    report += f"""
---

## 会话元数据
- **会话名称**: {session.session_name}
- **会话ID**: {session.session_id}
- **创建时间**: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- **最后更新**: {session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
- **当前阶段**: {session.current_stage.value}
- **使用AI模型**: {session.ai_model}
- **总消息数**: {len(session.messages)}

**报告生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**导出提示**: 此报告基于"全景式问题解决树"框架生成。方括号[...]部分需要根据上方对话记录填写具体内容。

> 灵光问题树工具 | 全景式问题解决框架 | 七步闭环 × 五大透镜 × 两大洞察
"""

    return report

def export_json(session: ProblemSession) -> str:
    """导出会话为JSON格式"""
    return json.dumps(session.to_dict(), ensure_ascii=False, indent=2)

def clear_all_sessions() -> bool:
    """清除所有会话数据"""
    try:
        if SESSIONS_FILE.exists():
            SESSIONS_FILE.unlink()
        return True
    except Exception:
        return False

def get_session_stats() -> Dict[str, Any]:
    """获取会话统计信息"""
    sessions = list_sessions()
    total_sessions = len(sessions)
    total_messages = sum(len(s.messages) for s in sessions)
    completed_sessions = len([s for s in sessions if s.current_stage.value == "已完成"])

    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "completed_sessions": completed_sessions,
        "avg_messages_per_session": total_messages / max(total_sessions, 1),
        "completion_rate": completed_sessions / max(total_sessions, 1)
    }

def extract_stage_messages(session, stage_enum):
    """提取指定阶段相关的对话消息

    Args:
        session: ProblemSession对象
        stage_enum: Stage枚举值

    Returns:
        List[Message]: 与该阶段相关的消息列表
    """
    from .models import Stage

    # 获取所有阶段列表
    all_stages = list(Stage)
    stage_index = all_stages.index(stage_enum)

    # 如果阶段是"已完成"，返回所有消息
    if stage_enum.value == "已完成":
        return session.messages

    # 根据消息数量分配阶段（简化逻辑）
    # 当前实现：每个阶段大约2条消息
    messages_per_stage = 2
    start_idx = stage_index * messages_per_stage
    end_idx = min((stage_index + 1) * messages_per_stage, len(session.messages))

    # 如果索引有效，返回切片
    if start_idx < len(session.messages):
        return session.messages[start_idx:end_idx]
    else:
        return []

def get_stage_summary(session, stage_enum):
    """获取阶段的摘要信息

    Args:
        session: ProblemSession对象
        stage_enum: Stage枚举值

    Returns:
        Dict: 包含阶段摘要信息的字典
    """
    stage_messages = extract_stage_messages(session, stage_enum)

    # 提取阶段的关键信息
    user_messages = [msg.content for msg in stage_messages if msg.role == "user"]
    assistant_messages = [msg.content for msg in stage_messages if msg.role == "assistant"]

    # 生成简单摘要
    summary = f"共{len(stage_messages)}条对话"
    if user_messages:
        summary += f"，用户提供了{len(user_messages)}个回答"
    if assistant_messages:
        summary += f"，AI提出了{len(assistant_messages)}个引导问题"

    # 提取关键内容（最后一条AI消息或用户消息）
    key_content = ""
    if assistant_messages:
        key_content = assistant_messages[-1][:100] + "..." if len(assistant_messages[-1]) > 100 else assistant_messages[-1]
    elif user_messages:
        key_content = user_messages[-1][:100] + "..." if len(user_messages[-1]) > 100 else user_messages[-1]

    return {
        "stage": stage_enum.value,
        "message_count": len(stage_messages),
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "summary": summary,
        "key_content": key_content,
        "messages": stage_messages
    }