"""
灵光问题树工具 v2 - 优化版
核心改进：
1. 即时预览模式 - 边拆解边展示
2. 卡片探索模式 - 每层一张卡片
3. Aha 时刻设计 - 30 秒内看到第一个洞察
4. 进度可视化 - 清晰知道进展
"""

import streamlit as st
import json
import datetime
import os
import sys
import time
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

# ========== 优化版 CSS 样式 ==========
st.markdown("""
<style>
    /* 全局渐变背景 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* 主容器 */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    }

    /* 标题 */
    h1 {
        color: #1E3A8A;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    h2, h3 {
        color: #374151;
    }

    /* Aha 卡片样式 */
    .aha-card {
        background: linear-gradient(135deg, #FDE68A 0%, #F59E0B 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #F59E0B;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .aha-card h4 {
        color: #92400E;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }

    .aha-card p {
        color: #78350F;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* 进度卡片 */
    .progress-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 2px solid #E5E7EB;
        transition: all 0.3s ease;
    }

    .progress-card.active {
        border-color: #3B82F6;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
    }

    .progress-card.completed {
        border-color: #10B981;
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
    }

    /* 按钮 */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }

    /* 对话气泡 */
    .chat-message {
        padding: 1rem;
        border-radius: 16px;
        margin: 0.5rem 0;
        max-width: 85%;
    }

    .chat-message.user {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        color: white;
        margin-left: auto;
    }

    .chat-message.assistant {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
    }

    /* 进度条 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3B82F6 0%, #10B981 100%);
    }

    /* 洞察金句 */
    .insight-quote {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        font-style: italic;
        color: #92400E;
    }

    /* 移动端适配 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        h1 {
            font-size: 1.8rem;
        }
        .chat-message {
            max-width: 95%;
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== 初始化会话状态 ==========
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "sessions" not in st.session_state:
    st.session_state.sessions = list_sessions()
if "ai_engine" not in st.session_state:
    try:
        st.session_state.ai_engine = ProblemTreeAI(backend="deepseek")
        st.session_state.ai_engine_initialized = True
    except Exception as e:
        st.session_state.ai_engine = None
        st.session_state.ai_engine_initialized = False
        st.session_state.ai_engine_error = str(e)
if "streaming_response" not in st.session_state:
    st.session_state.streaming_response = ""
if "current_step" not in st.session_state:
    st.session_state.current_step = 0

# ========== 辅助函数 ==========

def create_aha_card(title: str, content: str, icon: str = "💡"):
    """创建 Aha 洞察卡片"""
    st.markdown(f"""
    <div class="aha-card">
        <h4>{icon} {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_progress_card(step_name: str, status: str = "pending", content: str = ""):
    """创建进度卡片"""
    if status == "completed":
        st.markdown(f"""
        <div class="progress-card completed">
            <strong>✅ {step_name}</strong>
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)
    elif status == "active":
        st.markdown(f"""
        <div class="progress-card active">
            <strong>🔄 {step_name} - 进行中</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="progress-card">
            <strong>⏳ {step_name}</strong>
        </div>
        """, unsafe_allow_html=True)

def create_insight_quote(quote: str):
    """创建洞察金句"""
    st.markdown(f"""
    <div class="insight-quote">
        "{quote}"
    </div>
    """, unsafe_allow_html=True)

# ========== 主应用 ==========

def main():
    # 标题
    st.title("🌳 灵光问题树")
    st.markdown("**3 分钟，让复杂问题变清晰** - 基于全景式问题解决树框架，AI 引导你系统拆解任何复杂问题。")

    # 侧边栏
    with st.sidebar:
        st.header("🧭 导航")
        page = st.radio(
            "选择页面",
            ["新建会话", "当前会话", "历史会话", "设置"],
            label_visibility="collapsed"
        )

        st.divider()

        # 会话状态
        st.header("📊 会话状态")
        if st.session_state.current_session:
            st.success(f"当前问题：{st.session_state.current_session.problem_statement[:30]}...")
            st.caption(f"创建时间：{st.session_state.current_session.created_at}")
        else:
            st.info("无活跃会话")

    # 页面路由
    if page == "新建会话":
        show_new_session_page()
    elif page == "当前会话":
        show_current_session_page()
    elif page == "历史会话":
        show_history_page()
    elif page == "设置":
        show_settings_page()

# ========== 页面：新建会话 ==========

def show_new_session_page():
    st.header("✨ 开始你的问题拆解之旅")

    # 创建 Aha 时刻预览
    create_aha_card(
        "什么是 Aha 时刻？",
        "在 30 秒内看到第一个洞察，发现你从未想到的视角和层面！",
        "🎯"
    )

    with st.form("new_session_form"):
        problem = st.text_area(
            "💭 请描述你的初始问题",
            placeholder="例如：我工作效率低怎么办？如何提高团队凝聚力？",
            height=120,
            help="问题越具体，洞察越精准"
        )

        col1, col2 = st.columns(2)
        with col1:
            session_name = st.text_input("📝 会话名称（可选）", placeholder="默认为问题摘要")
        with col2:
            ai_model = st.selectbox(
                "🤖 选择 AI 模型",
                ["deepseek-chat", "claude-3-5-sonnet", "gpt-4"],
                index=0,
                help="DeepSeek 性价比高，Claude 质量最好"
            )

        # 提交按钮
        submitted = st.form_submit_button("🚀 开始拆解", use_container_width=True, type="primary")

        if submitted and problem.strip():
            if st.session_state.ai_engine is None:
                st.error("❌ AI 引擎不可用，请检查 API 密钥配置。")
            else:
                # 创建新会话
                new_session = ProblemSession(
                    problem_statement=problem,
                    session_name=session_name if session_name else problem[:30],
                    ai_model=ai_model
                )
                st.session_state.current_session = new_session
                st.session_state.sessions.append(new_session)
                save_session(new_session)

                # 重定向到当前会话页面
                st.success("✅ 会话创建成功！正在跳转到拆解页面...")
                time.sleep(1)
                st.rerun()
        elif submitted:
            st.warning("⚠️ 请输入问题描述")

    # 示例问题
    st.divider()
    st.subheader("💡 不知道从哪里开始？试试这些示例")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 工作效率低", use_container_width=True):
            st.session_state.example_problem = "我工作效率低，每天很忙但产出很少，怎么办？"
            st.rerun()
    with col2:
        if st.button("👥 团队沟通不畅", use_container_width=True):
            st.session_state.example_problem = "团队沟通不畅，信息不同步，经常重复工作，如何改善？"
            st.rerun()
    with col3:
        if st.button("🎯 职业发展方向", use_container_width=True):
            st.session_state.example_problem = "我对当前职业发展迷茫，不知道应该深耕还是转行，如何选择？"
            st.rerun()

    # 如果有示例问题，显示在输入框
    if "example_problem" in st.session_state:
        st.text_area(
            "💭 请描述你的初始问题",
            value=st.session_state.example_problem,
            height=120,
            key="example_problem_input"
        )

# ========== 页面：当前会话 ==========

def show_current_session_page():
    st.header("🌳 问题拆解")

    if not st.session_state.current_session:
        st.warning("⚠️ 没有活跃会话。请先创建一个新会话。")
        if st.button("➡️ 去新建会话"):
            st.rerun()
        return

    session = st.session_state.current_session

    # 顶部进度条
    stages = list(Stage)
    current_index = stages.index(session.current_stage)
    total_stages = len(stages)
    progress = current_index / (total_stages - 1)

    st.progress(progress)
    st.caption(f"进度：{current_index + 1}/{total_stages} - {session.current_stage.value}")

    st.divider()

    # 双栏布局：左侧对话，右侧进度
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("💬 对话")

        # 显示对话历史
        for msg in session.messages:
            if msg.role == "user":
                st.markdown(f"""
                <div class="chat-message user">
                    <strong>👤 你</strong><br>
                    {msg.content}
                </div>
                """, unsafe_allow_html=True)
            elif msg.role == "assistant":
                st.markdown(f"""
                <div class="chat-message assistant">
                    <strong>🤖 AI 教练</strong><br>
                    {msg.content}
                </div>
                """, unsafe_allow_html=True)

        # 用户输入
        st.divider()
        st.subheader("✍️ 你的回应")

        user_input = st.chat_input("请输入你的回答或思考...", key="user_chat")
        if user_input:
            if st.session_state.ai_engine is None:
                st.error("❌ AI 引擎不可用")
            else:
                # 添加用户消息
                session.add_message("user", user_input)

                # 显示"AI 正在思考"
                with st.spinner("🤔 AI 正在思考..."):
                    try:
                        ai_response = st.session_state.ai_engine.continue_session(
                            [{"role": msg.role, "content": msg.content} for msg in session.messages],
                            session.current_stage.value,
                            model=session.ai_model
                        )
                        session.add_message("assistant", ai_response)
                        session.update_stage()
                        save_session(session)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ AI 响应失败：{str(e)}")

        # 跳过按钮
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("⏭️ 跳过此步", use_container_width=True, type="secondary"):
                if st.session_state.ai_engine:
                    session.add_message("user", "[用户选择跳过]")
                    try:
                        ai_response = st.session_state.ai_engine.continue_session(
                            [{"role": msg.role, "content": msg.content} for msg in session.messages],
                            session.current_stage.value,
                            model=session.ai_model
                        )
                        session.add_message("assistant", ai_response)
                        session.update_stage()
                        save_session(session)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ AI 响应失败：{str(e)}")

    with right_col:
        st.subheader("📊 问题树进展")

        # 显示所有阶段的卡片
        stage_descriptions = {
            "0-问题淬炼": "聚焦核心问题",
            "1-问题定义": "结构化定义",
            "2-成功标准": "明确目标",
            "3-挑战评估": "识别障碍",
            "4-方案生成": "创造方案",
            "5-行动与迭代": "行动计划",
            "已完成": "完成"
        }

        for i, stage in enumerate(stages):
            if i < current_index:
                status = "completed"
            elif i == current_index:
                status = "active"
            else:
                status = "pending"

            stage_name = stage.value.split("-")[1] if "-" in stage.value else stage.value
            desc = stage_descriptions.get(stage.value, "")

            create_progress_card(f"第{i+1}步：{stage_name}", status, desc)

        # 快速导出
        st.divider()
        if st.button("📥 导出当前报告", use_container_width=True):
            report_md = export_markdown(session)
            st.download_button(
                label="⬇️ 下载报告",
                data=report_md,
                file_name=f"问题树报告_{session.session_name}.md",
                mime="text/markdown",
                use_container_width=True
            )

# ========== 页面：历史会话 ==========

def show_history_page():
    st.header("📚 历史会话")

    if not st.session_state.sessions:
        st.info("暂无历史会话。")
    else:
        total = len(st.session_state.sessions)
        completed = len([s for s in st.session_state.sessions if s.current_stage.value == "已完成"])
        st.caption(f"共 {total} 个会话，其中 {completed} 个已完成")

        for i, session in enumerate(st.session_state.sessions):
            with st.expander(f"{session.session_name} - {session.created_at.strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**问题:** {session.problem_statement[:100]}...")
                st.write(f"**阶段:** {session.current_stage.value}")
                st.write(f"**消息数:** {len(session.messages)}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("继续", key=f"continue_{i}"):
                        st.session_state.current_session = session
                        st.success(f"已切换到：{session.session_name}")
                        st.rerun()
                with col2:
                    report_md = export_markdown(session)
                    st.download_button("导出", data=report_md, file_name=f"问题树报告_{session.session_name}.md", key=f"export_{i}")
                with col3:
                    if st.button("删除", key=f"delete_{i}", type="secondary"):
                        if delete_session(session.session_id):
                            st.session_state.sessions = list_sessions()
                            st.success("已删除")
                            st.rerun()

# ========== 页面：设置 ==========

def show_settings_page():
    st.header("⚙️ 设置")

    st.subheader("🤖 AI 配置")
    api_key = st.text_input("API 密钥", type="password")
    default_model = st.selectbox("默认 AI 模型", ["deepseek-chat", "claude-3-5-sonnet", "gpt-4"], index=0)

    st.subheader("💾 数据管理")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("重新加载"):
            st.session_state.sessions = list_sessions()
            st.success(f"已加载 {len(st.session_state.sessions)} 个会话")
    with col2:
        if st.button("清除所有", type="secondary"):
            st.warning("⚠️ 这将删除所有数据！")
            if st.checkbox("我确认"):
                if clear_all_sessions():
                    st.session_state.sessions = []
                    st.success("已清除")
                    st.rerun()

    st.subheader("ℹ️ 关于")
    st.markdown("""
    **灵光问题树 v2.0**
    
    基于全景式问题解决树框架，融合流程推进与思维深度。
    
    - 七步闭环流程
    - 五大心智透镜
    - 两大洞察力标准
    """)

# ========== 启动应用 ==========

if __name__ == "__main__":
    main()
