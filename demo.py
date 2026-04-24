"""
演示模式 - 无需API密钥展示灵光问题树工具
"""

import streamlit as st
import datetime
import json
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="灵光问题树 - 演示模式",
    page_icon="🌳",
    layout="wide"
)

# 模拟会话数据
def create_demo_session():
    """创建演示会话"""
    demo_data = {
        "session_id": "demo_20250308_123456",
        "problem_statement": "我的工作效率低怎么办？",
        "session_name": "工作效率问题演示",
        "ai_model": "claude-3-5-sonnet (演示模式)",
        "created_at": "2026-03-08T12:00:00",
        "updated_at": "2026-03-08T12:30:00",
        "current_stage": "3-挑战评估",
        "messages": [
            {
                "role": "user",
                "content": "我的工作效率低怎么办？",
                "timestamp": "2026-03-08T12:01:00"
            },
            {
                "role": "assistant",
                "content": "感谢你提出这个问题。在直接寻找解决方案前，我们不妨先花点时间，确保我们正在解决最核心的问题。让我问你几个问题，帮你更清晰地聚焦。\n\n（证据）你说'效率低'，具体是指哪方面？是总是拖延，还是会议太多打断，或是完成任务耗时太长？有什么具体的例子吗？",
                "timestamp": "2026-03-08T12:01:30"
            },
            {
                "role": "user",
                "content": "我经常拖延重要的任务，总是在处理紧急但不重要的事情。",
                "timestamp": "2026-03-08T12:02:00"
            },
            {
                "role": "assistant",
                "content": "很好，这就更具体了。你提到'紧急但不重要的事情' - 这听起来像是优先级管理的问题。从另一个视角看，如果你的同事或上级来评价你的工作效率，他们会怎么说？他们的看法和你一致吗？",
                "timestamp": "2026-03-08T12:02:30"
            },
            {
                "role": "user",
                "content": "他们可能觉得我响应很快，但有些重要项目进度确实落后了。",
                "timestamp": "2026-03-08T12:03:00"
            },
            {
                "role": "assistant",
                "content": "感谢你分享这个视角。这很有帮助 - 我们发现了外部视角和内部感受的差异。你感觉自己效率低，但他人看到的是快速响应，只是重要项目进度落后。\n\n现在，我们来给这个问题画个清晰的像。请尝试用一句中性的语言描述它，比如'在……情况下，我面临着……挑战，导致了……结果'。",
                "timestamp": "2026-03-08T12:04:00"
            }
        ]
    }
    return demo_data

def create_demo_report():
    """创建演示报告"""
    return """# 问题树分析报告

## 一、原始问题
我的工作效率低怎么办？

## 二、淬炼后的核心问题
如何管理任务优先级，减少对紧急不重要事务的响应，以推进重要项目进展？

## 三、问题定义
- **结构化陈述**: 在当前工作环境中，我面临着紧急事务频繁打断、重要项目难以专注的挑战，导致了重要项目进度落后和工作满意度降低。
- **边界与范围**: 主要关注工作时间管理、任务优先级判断、工作流程优化。
- **关键利益相关方**: 我本人、直接领导、项目团队成员。

## 四、成功标准
- **定性描述（胜利画面）**: 每天有2小时不受干扰的深度工作时间，重要项目按计划推进，工作结束时感到充实而非疲惫。
- **关键指标（KPIs）**: 重要项目完成度提升30%，每日深度工作时间达到2小时，紧急事务处理时间减少50%。

## 五、关键挑战与风险评估
- **内部障碍**: 难以拒绝紧急请求，拖延重要任务的习惯，完美主义倾向。
- **外部障碍**: 频繁的会议和即时消息，紧急但不重要的任务分配，开放办公环境干扰。
- **最高风险项**: 无法建立有效的边界保护机制。

## 六、解决方案与行动计划
- **首选方案**: 实施"时间块保护"系统，结合任务优先级矩阵。
- **具体行动步骤**:
  1. （近期）明确定义每日的2小时深度工作时间段，通知同事，关闭通知。
  2. （中期）建立任务分类系统（重要/紧急矩阵），每周日晚规划下一周重点。
- **复盘与调整机制**: 每周五下午进行15分钟工作复盘，评估时间分配效果。

## 七、核心洞察（AI视角）
- **关于"回路"**: 识别了一个恶性循环：紧急事务打断→重要项目延期→更多紧急事务产生。解决方案是建立调节回路，保护深度工作时间。
- **关于"层级"**: 从事件层（"我又被打断了"）提升到结构层（"我的工作环境缺乏保护机制"）。
- **关键心智突破点**: 区分"响应快"和"进展快"，认识到为重要事务建立保护机制的必要性。

---

**报告生成时间**: 2026-03-08 12:30:00
**导出提示**: 此报告基于全景式问题解决树框架生成，可根据实际情况调整行动计划。
"""

# 主应用
st.title("🌳 灵光问题树 - 演示模式")
st.markdown("""
这是一个演示版本，展示了灵光问题树工具的核心功能。无需API密钥即可体验界面和流程。

**功能展示：**
- 问题解决流程（七步闭环）
- 对话式AI引导界面
- 会话历史管理
- 结构化报告导出
""")

# 侧边栏
with st.sidebar:
    st.header("演示导航")
    demo_page = st.radio(
        "选择演示页面",
        ["功能概览", "对话示例", "报告导出", "实际运行"]
    )

# 页面内容
if demo_page == "功能概览":
    st.header("功能概览")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 七步闭环")
        st.markdown("""
        1. 问题淬炼
        2. 问题定义
        3. 成功标准
        4. 挑战评估
        5. 方案生成
        6. 行动迭代
        7. 复盘优化
        """)

    with col2:
        st.markdown("### 🔍 五大透镜")
        st.markdown("""
        - **证据**: 具体事例
        - **视角**: 多方看法
        - **联系**: 模式规律
        - **猜想**: 重新定义
        - **相关**: 深层意义
        """)

    with col3:
        st.markdown("### 🧠 两大洞察")
        st.markdown("""
        - **看得远**: 系统回路
        - **看得透**: 问题层级

        从表面问题挖掘根本原因
        """)

    st.divider()
    st.subheader("技术架构")
    st.markdown("""
    - **前端**: Streamlit (Python)
    - **AI集成**: Claude/OpenAI API
    - **数据存储**: JSON文件
    - **导出格式**: Markdown/JSON/PDF
    """)

elif demo_page == "对话示例":
    st.header("对话示例")

    demo_data = create_demo_session()

    st.info("以下是AI引导问题解决的对话示例：")

    # 显示对话
    for i, msg in enumerate(demo_data["messages"]):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"**👤 你:** {msg['content']}")
        else:
            with st.chat_message("assistant"):
                st.markdown(f"**🤖 AI教练:**")
                st.markdown(msg["content"])

    st.divider()
    st.subheader("分析说明")
    st.markdown("""
    在这个示例中，AI使用了以下引导技巧：

    1. **问题淬炼**: 从模糊的"效率低"聚焦到具体的"优先级管理"
    2. **视角转换**: 询问同事的看法，发现外部视角差异
    3. **结构定义**: 引导用户用中性的语言重新描述问题

    这是"全景式问题解决树"框架的典型应用。
    """)

elif demo_page == "报告导出":
    st.header("报告导出示例")

    demo_report = create_demo_report()

    st.info("这是AI生成的结构化问题树报告：")

    # 显示报告预览
    with st.expander("📄 查看完整报告", expanded=True):
        st.markdown(demo_report)

    st.divider()
    st.subheader("导出选项")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="📥 下载Markdown",
            data=demo_report,
            file_name="问题树报告_演示示例.md",
            mime="text/markdown"
        )

    with col2:
        st.download_button(
            label="📊 下载JSON",
            data=json.dumps(create_demo_session(), indent=2, ensure_ascii=False),
            file_name="会话数据_演示示例.json",
            mime="application/json"
        )

    with col3:
        st.info("PDF导出需安装wkhtmltopdf")

elif demo_page == "实际运行":
    st.header("实际运行说明")

    st.success("要运行完整版本，请按以下步骤操作：")

    st.markdown("""
    ### 步骤1: 安装依赖
    ```bash
    pip install -r requirements.txt
    ```

    ### 步骤2: 配置API密钥
    1. 复制 `.env.example` 为 `.env`
    2. 在 `.env` 中添加你的API密钥：
       - `ANTHROPIC_API_KEY` (Claude)
       - `OPENAI_API_KEY` (OpenAI)

    ### 步骤3: 启动应用
    ```bash
    streamlit run app.py
    ```

    或使用启动脚本：
    - Windows: `run.bat`
    - Linux/Mac: `./run.sh`
    """)

    st.divider()
    st.subheader("支持的AI模型")
    st.markdown("""
    - **Claude**: claude-3-5-sonnet, claude-3-haiku
    - **OpenAI**: gpt-4, gpt-3.5-turbo
    - **自定义后端**: 可扩展支持其他模型
    """)

# 页脚
st.divider()
st.caption("演示版本 v0.1.0 | 灵光问题树工具 | 基于全景式问题解决树框架")