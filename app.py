"""
灵光问题树工具 - Streamlit 应用
基于全景式问题解决树框架，AI引导用户拆解问题，记录历史并支持导出。
"""

import streamlit as st
import json
import datetime
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加模块路径
sys.path.append(str(Path(__file__).parent))

from modules.ai_module import ProblemTreeAI
from modules.models import ProblemSession, Message, Stage
from modules.utils import save_session, load_session, list_sessions, export_markdown, delete_session, clear_all_sessions, get_stage_summary

# 页面配置
st.set_page_config(
    page_title="灵光问题树",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 增强沉浸感和移动端适配
st.markdown("""
<style>
    /* 主容器样式 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 标题样式 */
    h1, h2, h3 {
        color: #1E3A8A;
        font-weight: 600;
    }

    h1 {
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }

    /* 卡片样式 */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .stMetric label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500;
    }

    .stMetric div {
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 700;
    }

    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 100%);
    }

    .css-1d391kg .stRadio label {
        color: white !important;
        font-weight: 500;
    }

    .css-1d391kg .stRadio div[role="radiogroup"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
    }

    .css-1d391kg .stRadio div[data-baseweb="radio"] {
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        border-radius: 6px;
        transition: all 0.3s ease;
    }

    .css-1d391kg .stRadio div[data-baseweb="radio"]:hover {
        background: rgba(255, 255, 255, 0.15);
    }

    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3B82F6 0%, #10B981 100%);
    }

    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* 对话框样式 */
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* 移动端适配 */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        h1 {
            font-size: 1.5rem;
        }

        .stMetric {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .stMetric div {
            font-size: 1.2rem !important;
        }

        /* 在移动端改为单列布局 */
        .element-container > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }

        /* 调整侧边栏 */
        .css-1d391kg {
            width: 100% !important;
        }
    }

    /* 沉浸感增强 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }

    /* 卡片阴影效果 */
    .stExpander {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }

    /* 状态指示器 */
    .stSuccess {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        border: none;
    }

    .stInfo {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        border: none;
    }

    .stWarning {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        border: none;
    }

    /* 对话消息特定样式 */
    [data-testid="stChatMessage"] {
        border-radius: 16px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }

    [data-testid="stChatMessage"]:nth-child(odd) {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
    }

    [data-testid="stChatMessage"]:nth-child(even) {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "sessions" not in st.session_state:
    st.session_state.sessions = list_sessions()
if "ai_engine" not in st.session_state:
    st.session_state.ai_engine = ProblemTreeAI(backend="deepseek")

# 标题和描述
st.title("🌳 灵光问题树")
st.markdown("""
基于**全景式问题解决树框架**，AI引导你系统拆解任何复杂问题，生成结构化行动方案。
""")

# 侧边栏
with st.sidebar:
    st.header("导航")
    page = st.radio(
        "选择页面",
        ["新建会话", "当前会话", "历史会话", "设置"]
    )

    st.divider()

    st.header("会话状态")
    if st.session_state.current_session:
        st.info(f"当前问题: {st.session_state.current_session.problem_statement[:50]}...")
        st.caption(f"创建时间: {st.session_state.current_session.created_at}")
        st.caption(f"当前阶段: {st.session_state.current_session.current_stage.value}")
    else:
        st.warning("无活跃会话")

    st.divider()

    st.caption("版本 0.1.0 | 支持DeepSeek/Claude/OpenAI")

# 页面路由
if page == "新建会话":
    st.header("新建问题树会话")

    with st.form("new_session_form"):
        problem = st.text_area(
            "请描述你的初始问题",
            placeholder="例如：我工作效率低怎么办？",
            height=100
        )

        col1, col2 = st.columns(2)
        with col1:
            session_name = st.text_input("会话名称（可选）", placeholder="默认为问题摘要")
        with col2:
            ai_model = st.selectbox(
                "选择AI模型",
                ["deepseek-chat", "claude-3-5-sonnet", "gpt-4", "claude-3-haiku"],
                index=0
            )

        submitted = st.form_submit_button("开始分析")

        if submitted and problem.strip():
            # 创建新会话
            new_session = ProblemSession(
                problem_statement=problem,
                session_name=session_name if session_name else problem[:30],
                ai_model=ai_model
            )
            st.session_state.current_session = new_session
            st.session_state.sessions.append(new_session)
            save_session(new_session)

            # 初始化AI引导
            ai_response = st.session_state.ai_engine.start_session(
                problem,
                model=ai_model
            )
            new_session.add_message("assistant", ai_response)
            save_session(new_session)

            st.success("会话创建成功！请切换到'当前会话'页面继续。")
            st.rerun()
        elif submitted:
            st.error("请输入问题描述")

elif page == "当前会话":
    st.header("当前会话")

    if not st.session_state.current_session:
        st.warning("没有活跃会话。请从侧边栏选择'新建会话'创建一个新会话。")
    else:
        session = st.session_state.current_session

        # 显示会话信息（顶部指标）
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("当前阶段", session.current_stage.value)
        with col2:
            st.metric("消息数量", len(session.messages))
        with col3:
            st.metric("创建时间", session.created_at.strftime("%Y-%m-%d %H:%M"))

        st.divider()

        # 创建左右两列布局
        left_col, right_col = st.columns([2, 1])

        # 左侧列：对话历史
        with left_col:
            st.subheader("对话历史")
            for msg in session.messages:
                with st.chat_message(msg.role):
                    st.markdown(msg.content)

            # 用户输入
            if session.current_stage.value != "已完成":
                st.divider()
                st.subheader("你的回应")

                user_input = st.chat_input("请输入你的回答或思考...")
                if user_input:
                    # 添加用户消息
                    session.add_message("user", user_input)

                    # 获取AI响应
                    with st.spinner("AI正在思考..."):
                        ai_response = st.session_state.ai_engine.continue_session(
                            [{"role": msg.role, "content": msg.content} for msg in session.messages],
                            session.current_stage.value,
                            model=session.ai_model
                        )
                        session.add_message("assistant", ai_response)

                    # 更新会话阶段
                    session.update_stage()
                    save_session(session)

                    st.rerun()

                # 跳过当前问题按钮
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("跳过此问题", type="secondary", use_container_width=True):
                        # 添加一个空的用户消息来推进阶段
                        session.add_message("user", "[用户选择跳过此问题]")

                        # 获取AI响应
                        with st.spinner("AI正在思考..."):
                            ai_response = st.session_state.ai_engine.continue_session(
                                [{"role": msg.role, "content": msg.content} for msg in session.messages],
                                session.current_stage.value,
                                model=session.ai_model
                            )
                            session.add_message("assistant", ai_response)

                        # 更新会话阶段
                        session.update_stage()
                        save_session(session)
                        st.rerun()
            else:
                st.success("🎉 问题树构建完成！请到'导出报告'页面生成最终报告。")

        # 右侧列：进展更新模块
        with right_col:
            st.subheader("问题树进展")

            # 阶段进度条
            stages = list(Stage)
            current_index = stages.index(session.current_stage)
            total_stages = len(stages)
            progress_percentage = (current_index / (total_stages - 1)) * 100

            st.progress(progress_percentage / 100)
            st.caption(f"进度: {progress_percentage:.0f}% ({session.current_stage.value})")

            st.divider()

            # 阶段映射到描述
            stage_descriptions = {
                "0-问题淬炼": "通过提问聚焦核心问题，确保解决的是真问题",
                "1-问题定义": "精准结构化定义问题，明确边界和范围",
                "2-成功标准": "设定清晰、可衡量的解决目标和成功画面",
                "3-挑战评估": "识别内部和外部障碍，评估主要风险",
                "4-方案生成": "创造并选择行动路径，头脑风暴多种方案",
                "5-行动与迭代": "规划近期行动并建立复盘机制",
                "已完成": "问题树构建完成，可导出报告"
            }

            # 显示所有阶段的卡片
            for i, stage in enumerate(stages):
                # 确定阶段状态
                if i < current_index:
                    status = "✅ 已完成"
                    status_color = "success"
                    stage_icon = "✅"
                elif i == current_index:
                    status = "🔄 进行中"
                    status_color = "info"
                    stage_icon = "🔄"
                else:
                    status = "⏳ 未开始"
                    status_color = "secondary"
                    stage_icon = "⏳"

                # 获取阶段摘要信息
                stage_summary = get_stage_summary(session, stage)

                # 创建阶段卡片（默认展开）
                with st.expander(f"{stage_icon} {stage.value} - {status}", expanded=True):
                    # 显示阶段描述
                    stage_desc = stage_descriptions.get(stage.value, "")
                    st.caption(stage_desc)

                    # 显示阶段摘要
                    st.markdown(f"**摘要**: {stage_summary['summary']}")

                    # 如果阶段有内容，显示关键对话
                    if stage_summary['message_count'] > 0:
                        st.divider()
                        st.markdown("**关键对话片段:**")

                        # 显示该阶段的消息（最多显示3条）
                        display_messages = stage_summary['messages'][-3:] if len(stage_summary['messages']) > 3 else stage_summary['messages']
                        for msg in display_messages:
                            role_icon = "👤" if msg.role == "user" else "🤖" if msg.role == "assistant" else "⚙️"
                            role_text = "你" if msg.role == "user" else "AI教练" if msg.role == "assistant" else "系统"

                            # 显示消息预览（可展开查看完整内容）
                            content_preview = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
                            with st.expander(f"{role_icon} {role_text}: {content_preview}", expanded=False):
                                st.markdown(msg.content)

                    # 如果是当前阶段，添加跳过按钮
                    if i == current_index and stage.value != "已完成":
                        st.divider()
                        if st.button("跳过此问题", key=f"skip_{stage.value}", use_container_width=True, type="secondary"):
                            # 添加一个空的用户消息来推进阶段
                            session.add_message("user", "[用户选择跳过此问题]")

                            # 获取AI响应
                            with st.spinner("AI正在思考..."):
                                ai_response = st.session_state.ai_engine.continue_session(
                                    [{"role": msg.role, "content": msg.content} for msg in session.messages],
                                    session.current_stage.value,
                                    model=session.ai_model
                                )
                                session.add_message("assistant", ai_response)

                            # 更新会话阶段
                            session.update_stage()
                            save_session(session)
                            st.rerun()

            # 快速操作
            st.divider()
            st.markdown("### 快速操作")

            # 导出当前会话报告
            if st.button("📥 导出当前报告", use_container_width=True):
                report_md = export_markdown(session)
                st.download_button(
                    label="下载报告",
                    data=report_md,
                    file_name=f"问题树报告_{session.session_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

elif page == "历史会话":
    st.header("历史会话")

    if not st.session_state.sessions:
        st.info("暂无历史会话。")
    else:
        # 统计信息
        total = len(st.session_state.sessions)
        completed = len([s for s in st.session_state.sessions if s.current_stage.value == "已完成"])
        st.caption(f"共 {total} 个会话，其中 {completed} 个已完成")

        # 会话列表
        for i, session in enumerate(st.session_state.sessions):
            with st.expander(f"{session.session_name} - {session.created_at.strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**问题:** {session.problem_statement[:100]}...")
                st.write(f"**阶段:** {session.current_stage.value}")
                st.write(f"**消息数:** {len(session.messages)}")
                st.write(f"**最后更新:** {session.updated_at.strftime('%Y-%m-%d %H:%M')}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("继续会话", key=f"continue_{i}"):
                        st.session_state.current_session = session
                        st.success(f"已切换到会话: {session.session_name}")
                        st.rerun()
                with col2:
                    # 导出按钮
                    report_md = export_markdown(session)
                    st.download_button(
                        label="导出报告",
                        data=report_md,
                        file_name=f"问题树报告_{session.session_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key=f"export_{i}"
                    )
                with col3:
                    if st.button("删除", key=f"delete_{i}", type="secondary"):
                        if delete_session(session.session_id):
                            st.session_state.sessions = list_sessions()
                            st.success(f"已删除会话: {session.session_name}")
                            st.rerun()
                        else:
                            st.error("删除失败")

elif page == "设置":
    st.header("设置")

    st.subheader("AI配置")
    api_key = st.text_input("API密钥", type="password")
    default_model = st.selectbox(
        "默认AI模型",
        ["deepseek-chat", "claude-3-5-sonnet", "gpt-4", "claude-3-haiku"],
        index=0
    )

    st.subheader("数据管理")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("重新加载会话数据"):
            st.session_state.sessions = list_sessions()
            st.success(f"已重新加载 {len(st.session_state.sessions)} 个会话")

    with col2:
        if st.button("清除所有会话数据", type="secondary"):
            st.warning("这将删除所有历史会话，不可恢复！")
            confirm = st.checkbox("我确认要永久删除所有数据")
            if confirm and st.button("确认删除", type="primary"):
                if clear_all_sessions():
                    st.session_state.sessions = []
                    st.session_state.current_session = None
                    st.success("所有会话数据已清除")
                    st.rerun()
                else:
                    st.error("清除数据时出错")

    st.subheader("关于")
    st.markdown("""
    **灵光问题树工具 v0.1.0**

    基于全景式问题解决树框架开发。

    框架特点：
    - 七步闭环流程
    - 五大心智透镜
    - 两大洞察力标准

    开发中，欢迎反馈。
    """)

# 页脚
st.divider()
st.caption("© 2026 灵光问题树工具 | 基于AI构建 | 全景式问题解决树框架")