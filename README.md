# 灵光问题树工具 v2.0

基于全景式问题解决树框架的 AI 引导问题拆解工具。支持两种分析模式，适配不同场景。

---

## 🌐 在线体验（Vercel 部署）

**https://problem-tree-tool.vercel.app**

无需安装，打开浏览器就能用。在 Vercel Dashboard → Settings → Environment Variables 配置 API 密钥。

---

## 两种分析模式

### 💬 多轮对话模式（适合深度思考）

- AI 逐步引导，七步闭环流程
- 适合需要启发的复杂问题
- 可中途跳过或直接完成

### 🌊 问题瀑布模式（适合快速输出）

- 一键生成完整分析框架
- 包含核心问题、目标设定、风险识别、解决方案、行动计划
- 适合直接可用

---

## 项目结构

```
problem-tree-tool/
├── streamlit_app/           # Streamlit 版（本地/Streamlit Cloud）
│   ├── app.py              # 对话模式主应用
│   └── app_v2.py           # 双模式主应用
├── vercel_app/             # Vercel 版（FastAPI + 原生 HTML/JS）
│   ├── api/index.py         # FastAPI Serverless Functions（所有 API 路由）
│   ├── index.html           # 前端（原生 HTML/JS，无框架）
│   └── requirements.txt     # Vercel 部署依赖
├── core/                   # 共享核心逻辑
│   ├── ai_core.py          # AI 后端（Claude/OpenAI/DeepSeek）
│   ├── prompt_engine.py     # 提示词引擎
│   ├── models_core.py       # 数据模型
│   └── session_store.py     # 会话存储
├── app.py                  # (旧) 对话模式主应用
├── app_v2.py               # (旧) 双模式主应用
├── modules/                # (旧) 原始模块
├── vercel.json             # Vercel 部署配置
└── requirements.txt        # 本地开发依赖
```

---

## 快速开始

### Vercel 在线版（推荐）

1. Fork 此仓库
2. Vercel 导入项目
3. 配置环境变量：`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `DEEPSEEK_API_KEY`
4. Deploy

### 本地开发

#### Vercel 版本（FastAPI）

```bash
pip install -r vercel_app/requirements.txt
./run_vercel.sh
# 访问 http://localhost:8000
```

#### Streamlit 版本

```bash
pip install -r requirements.txt
streamlit run streamlit_app/app_v2.py
# 访问 http://localhost:8501
```

---

## Vercel 环境变量配置

在 Vercel Dashboard → Settings → Environment Variables 添加：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | Claude API 密钥 | `sk-ant-...` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-...` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-...` |

至少配置一个即可使用。

---

## 部署到 Vercel

### 一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/lj22503/problem-tree-tool)

### 手动部署

```bash
npm install -g vercel
vercel login
vercel --prod
```

---

## 功能特点

- **双模式支持**：对话模式 + 瀑布模式
- **AI 引导问题拆解**：基于七步闭环流程
- **五大心智透镜**：证据、视角、联系、猜想、相关
- **会话历史管理**：侧边栏保存所有会话
- **多 AI 模型支持**：Claude / OpenAI / DeepSeek，可随时切换
- **会话导出**：Markdown 格式报告

---

## 七步闭环流程

0. **问题淬炼** — 衍生和聚焦真问题
1. **问题定义** — 精准结构化定义问题
2. **成功标准** — 设定清晰可衡量的目标
3. **挑战评估** — 识别障碍与风险
4. **方案生成** — 创造并选择行动路径
5. **行动与迭代** — 规划近期行动并建立复盘机制

---

## 许可证

MIT
