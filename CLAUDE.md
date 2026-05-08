# CLAUDE.md

> 技术 Agent 的项目级上下文。每个子技术 Agent 读这个文件自主工作。

---

## 项目概述

**游刃** — 基于《庄子》庖丁解牛典故的 AI 问题拆解工具
**GitHub**: https://github.com/lj22503/problem-tree-tool
**在线地址**: https://problemmap.mangofolio.com
**定位**：面向所有人的思维陪练工具，让复杂问题游刃有余

**两种模式**：
- 有人带路（Coach）：AI 逐步引导，7步闭环，像顾问一样陪你拆解
- 自己开图（Map）：直接输出完整分析报告，快速直达

**核心用户场景**：年终复盘、谈薪资、毕业选择、理财省钱、家庭沟通、方向感缺失

---

## 技术栈

### 核心

| 类别 | 技术 |
|------|------|
| AI | Claude / OpenAI / DeepSeek（通过 `core/ai_core.py` 统一封装）|
| 数据模型 | Pydantic 2.0+ |
| 会话存储 | JSON 文件（`data/sessions.json`）|

### 入口（两个版本）

| 版本 | 入口 | 说明 |
|------|------|------|
| Streamlit（本地） | `streamlit_app/app_v2.py` | pip install 后 `streamlit run` |
| Vercel（线上） | `vercel_app/` | FastAPI + 原生 HTML/JS |

### 共享核心（`core/`）

| 文件 | 说明 |
|------|------|
| `core/ai_core.py` | AI 客户端统一封装 |
| `core/prompt_engine.py` | 七步流程提示词管理 |
| `core/models_core.py` | Pydantic 数据模型 |
| `core/session_store.py` | 会话持久化 |

---

## 项目结构

```
problem-tree-tool/
├── CLAUDE.md              ← 你在这里（项目级上下文）
├── core/                  ← 共享核心逻辑（优先使用）
│   ├── ai_core.py
│   ├── prompt_engine.py
│   ├── models_core.py
│   └── session_store.py
├── streamlit_app/         ← Streamlit 版（本地开发）
│   └── app_v2.py         ← 双模式主应用
├── vercel_app/           ← Vercel 版
│   ├── api/              ← FastAPI Routes
│   ├── index.html         ← 前端
│   └── requirements.txt
├── modules/              ← 旧版模块（已废弃，待迁移到 core/）
│   ├── models.py
│   ├── utils.py
│   ├── ai_module.py
│   └── prompts_waterfall.py
├── requirements.txt       ← Streamlit 版依赖
├── vercel_app/requirements.txt
├── test_basic.py         ← 基本功能测试
└── data/                 ← 会话数据（sessions.json）
```

---

## 常用命令

```bash
# Streamlit 本地开发
pip install -r requirements.txt
streamlit run streamlit_app/app_v2.py
# 访问 http://localhost:8501

# Vercel 本地开发
pip install -r vercel_app/requirements.txt
./run_vercel.sh
# 访问 http://localhost:8000

# 基本功能测试
python test_basic.py

# 语法检查
python -m py_compile core/*.py modules/*.py

# pytest（如果安装了测试依赖）
pytest tests/ -v
```

---

## 代码规范

- Python 3.11+
- 函数/变量：`snake_case`
- 类：`PascalCase`
- Pydantic models：字段加类型注解
- AI 调用：统一通过 `core/ai_core.py`，不要直接调 API

---

## 环境变量

```
# .env（不提交到 git）
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
DEEPSEEK_API_KEY=sk-xxx
```

---

## 技术 Agent 工作流

当主 Agent 通过 `delegate_task` 调度技术 Agent 时：

1. **探索** — 了解 `core/` 和 `streamlit_app/` 结构
2. **规划** — 设计实现方案（不写代码）
3. **实现** — 优先改 `core/`，不要改 `modules/`（旧代码）
4. **验证** — `python test_basic.py` 或 `python -m py_compile`
5. **交付** — 报告修改的文件

---

## 质量标准

- `python test_basic.py` 通过
- 不破坏现有功能
- 优先使用 `core/` 而非 `modules/`
- Commit message：`feat:`, `fix:`, `refactor:`

---

## 注意事项

- `modules/` 是旧版代码，可以参考但不要新增功能进去
- 会话数据在 `data/sessions.json`，重构前先备份
- `core/` 是新结构，所有新功能都往 `core/` 里加
