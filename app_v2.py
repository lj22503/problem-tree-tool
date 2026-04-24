"""
灵光问题树工具 v2.0 - Streamlit 应用
支持两种模式：
1. 多轮对话模式 - AI 引导式，适合个人教练和启发
2. 问题瀑布模式 - 一键生成完整框架，适合快速分析
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
from modules.prompts_waterfall import WaterfallPromptEngine

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="灵光问题树 v2.0",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #1E3A8A;
        font-weight: 600;
    }

    h1 {
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .mode-selector {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        color: white;
    }

    .mode-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }

    .mode-card h3 {
        color: white;
        margin-bottom: 0.5rem;
    }

    .mode-card p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
    }

    .waterfall-output {
        background: #f8f9fa;
        border-left: 4px solid #3B82F6;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if 'mode' not in st.session_state:
    st.session_state.mode = 'dialog'  # 'dialog' 或 'waterfall'
if 'ai' not in st.session_state:
    st.session_state.ai = None
if 'waterfall_result' not in st.session_state:
    st.session_state.waterfall_result = None

# 标题
st.title("🌳 灵光问题树 v2.0")
st.markdown("AI 驱动的系统性问题分析与解决方案生成工具")

# 模式选择
st.markdown("""
<div class="mode-selector">
    <h2 style="color: white; margin-bottom: 1rem;">选择分析模式</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div class="mode-card">
            <h3>💬 多轮对话模式</h3>
            <p>AI 引导式，逐步拆解问题</p>
            <p><strong>适合：</strong>个人教练、深度启发、需要思考过程</p>
        </div>
        <div class="mode-card">
            <h3>🌊 问题瀑布模式</h3>
            <p>一键生成完整分析框架</p>
            <p><strong>适合：</strong>快速分析、结构化报告、直接可用</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 模式切换
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 多轮对话模式", use_container_width=True, key="btn_dialog"):
        st.session_state.mode = 'dialog'
        st.rerun()
with col2:
    if st.button("🌊 问题瀑布模式", use_container_width=True, key="btn_waterfall"):
        st.session_state.mode = 'waterfall'
        st.rerun()

st.divider()

# ========== 多轮对话模式 ==========
if st.session_state.mode == 'dialog':
    st.header("💬 多轮对话模式")
    st.markdown("AI 会按照七步闭环流程，逐步引导你拆解问题。")

    # 初始化 AI
    if st.session_state.ai is None:
        try:
            st.session_state.ai = ProblemTreeAI()
        except Exception as e:
            st.error(f"AI 初始化失败：{e}")
            st.info("请检查 .env 文件中的 API 密钥配置")
            st.stop()

    # 会话管理
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None

    # 开始新会话
    if not st.session_state.current_session:
        st.subheader("开始新问题")
        initial_question = st.text_area(
            "你想要分析的问题是什么？",
            placeholder="例如：我的产品用户留存率一直在掉，怎么办？",
            height=100
        )

        if st.button("🚀 开始分析", type="primary"):
            if initial_question:
                st.session_state.current_session = ProblemSession(initial_question)
                st.session_state.ai.start_session(initial_question)
                st.rerun()
            else:
                st.warning("请输入问题")

    # 对话进行中
    else:
        session = st.session_state.current_session

        # 显示进度
        stages = ["问题淬炼", "问题定义", "成功标准", "挑战评估", "方案生成", "行动迭代"]
        current_stage_idx = len([m for m in session.messages if m.role == 'assistant']) // 2
        progress = current_stage_idx / len(stages)
        st.progress(progress)
        st.caption(f"当前阶段：{stages[min(current_stage_idx, len(stages)-1)]} ({int(progress*100)}%)")

        # 显示对话历史
        for message in session.messages:
            with st.chat_message(message.role):
                st.write(message.content)

        # 用户输入
        if user_input := st.chat_input("输入你的回答..."):
            # 添加用户消息
            session.messages.append(Message(role='user', content=user_input))
            st.session_state.ai.add_message(user_input)

            # 获取 AI 响应
            with st.spinner("AI 思考中..."):
                try:
                    ai_response = st.session_state.ai.get_next_response()
                    session.messages.append(Message(role='assistant', content=ai_response))

                    # 检查是否完成
                    if st.session_state.ai.is_complete():
                        st.success("🎉 分析完成！可以在侧边栏导出报告。")
                except Exception as e:
                    st.error(f"AI 响应失败：{e}")

            st.rerun()

        # 导出选项
        if st.session_state.ai.is_complete():
            st.subheader("📥 导出报告")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 导出 Markdown", use_container_width=True):
                    markdown = export_markdown(session)
                    st.download_button(
                        "下载报告",
                        markdown,
                        file_name=f"问题树报告-{datetime.datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown"
                    )
            with col2:
                if st.button("🗑️ 删除会话", use_container_width=True, type="secondary"):
                    st.session_state.current_session = None
                    st.rerun()

# ========== 问题瀑布模式 ==========
elif st.session_state.mode == 'waterfall':
    st.header("🌊 问题瀑布模式")
    st.markdown("输入问题，AI 一次性生成完整的分析框架。")

    # 初始化瀑布引擎
    waterfall_engine = WaterfallPromptEngine()

    # 问题输入
    st.subheader("输入你的问题")
    question = st.text_area(
        "你想要分析的问题是什么？",
        placeholder="例如：在 AI 时代，如何有效管理个人'上下文'（Context）？",
        height=150,
        key="waterfall_question"
    )

    # 额外上下文（可选）
    with st.expander("➕ 添加额外上下文（可选）"):
        context_notes = st.text_area(
            "补充信息（如背景、约束条件、相关因素等）",
            placeholder="例如：我每天接触大量信息，但很难整合...",
            height=100,
            key="waterfall_context"
        )

    # 生成按钮
    if st.button("🌊 生成完整分析", type="primary", key="btn_generate_waterfall"):
        if question:
            with st.spinner("AI 正在生成完整分析框架，这可能需要 1-2 分钟..."):
                try:
                    # 构建提示词
                    context = {}
                    if context_notes:
                        context['额外说明'] = context_notes

                    prompt = waterfall_engine.build_waterfall_prompt(question, context)
                    system_prompt = waterfall_engine.get_system_prompt()

                    # 调用 AI
                    if st.session_state.ai is None:
                        st.session_state.ai = ProblemTreeAI()

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]

                    from modules.ai_module import AIBackend
                    backend = st.session_state.ai.current_backend
                    if backend:
                        result = backend.generate_response(messages, max_tokens=6000)
                        st.session_state.waterfall_result = result
                    else:
                        st.error("AI 后端未初始化")
                        st.stop()

                except Exception as e:
                    st.error(f"生成失败：{e}")
                    st.stop()

            # 显示结果
            if st.session_state.waterfall_result:
                st.success("✅ 分析完成！")

                # 显示完整报告
                st.markdown(st.session_state.waterfall_result)

                # 导出选项
                st.divider()
                st.subheader("📥 导出选项")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.download_button(
                        "📄 下载 Markdown",
                        st.session_state.waterfall_result,
                        file_name=f"思维树报告-{datetime.datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    ):
                        pass
                with col2:
                    if st.button("📋 复制到剪贴板", use_container_width=True):
                        st.code(st.session_state.waterfall_result, language="markdown")
                        st.info("已显示 Markdown 源码，可手动复制")
                with col3:
                    if st.button("🔄 重新分析", use_container_width=True, type="secondary"):
                        st.session_state.waterfall_result = None
                        st.rerun()
        else:
            st.warning("请输入问题")

    # 显示历史结果（如果有）
    elif st.session_state.waterfall_result:
        st.success("✅ 上次分析结果")
        st.markdown(st.session_state.waterfall_result)

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("⚙️ 设置")

    # API 状态
    st.subheader("API 状态")
    if st.session_state.ai and st.session_state.ai.current_backend:
        st.success(f"✅ 已连接：{type(st.session_state.ai.current_backend).__name__}")
    else:
        st.warning("⚠️ 未连接 API")
        st.info("请检查 .env 文件配置")

    # 历史会话
    st.subheader("📚 历史会话")
    sessions = list_sessions()
    if sessions:
        for session_id, session_data in sessions.items():
            if st.button(f"📄 {session_data['question'][:30]}...", key=f"load_{session_id}"):
                st.session_state.current_session = load_session(session_id)
                st.rerun()
    else:
        st.info("暂无历史会话")

    # 帮助
    st.subheader("❓ 帮助")
    st.markdown("""
    **多轮对话模式**：
    - AI 逐步引导
    - 适合深度思考
    - 可中途修改

    **问题瀑布模式**：
    - 一次性生成
    - 适合快速分析
    - 直接导出使用
    """)

    # 关于
    st.markdown("---")
    st.markdown("""
    **灵光问题树 v2.0**

    基于全景式问题解决树框架

    [GitHub](https://github.com/lj22503/problem-tree-tool)
    """)
