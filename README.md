# 灵光问题树工具 v2.0

基于全景式问题解决树框架的 AI 引导问题拆解工具。支持两种分析模式，适配不同场景。

## 🌐 在线体验

**https://problem-tree-tool.vercel.app**

无需安装，打开浏览器就能用。

需要 AI API 密钥（Claude/OpenAI/DeepSeek）。

---

## 🎯 两种分析模式

### 💬 多轮对话模式（适合个人教练）
- AI 逐步引导，七步闭环流程
- 适合深度思考、需要启发的场景
- 可中途修改方向，灵活调整

### 🌊 问题瀑布模式（适合快速分析）
- 一次性生成完整分析框架
- 包含：核心问题、目标设定、风险识别、解决方案、行动计划、多维度分析
- 适合快速输出、结构化报告、直接可用

## 功能特点

- **双模式支持**: 对话模式 + 瀑布模式
- **AI 引导问题拆解**: 基于七步闭环流程
- **五大心智透镜**: 证据、视角、联系、猜想、相关
- **两大洞察力标准**: 看得远（回路）、看得透（层级）
- **会话历史管理**: 保存所有问题树会话
- **多种导出格式**: Markdown、JSON，支持 PDF 转换
- **多 AI 模型支持**: Claude、OpenAI、DeepSeek

## 快速开始

### 方式一：在线版（最快）⭐

访问：**https://problem-tree-tool.vercel.app**

无需安装，打开浏览器就能用。

需要 AI API 密钥。

### 方式二：本地版（推荐）

```bash
# 克隆项目
git clone https://github.com/lj22503/problem-tree-tool.git
cd problem-tree-tool

# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
cp .env.example .env
# 编辑 .env 文件，添加你的 API 密钥

# 运行（双模式版本，推荐）
streamlit run app_v2.py

# 运行（仅对话模式）
streamlit run app.py
```

## 使用场景

### 💬 多轮对话模式适合：
- 个人成长问题（职业规划、习惯养成）
- 复杂决策（创业方向、产品定位）
- 需要深度思考的问题
- 想要 AI 引导式启发

### 🌊 问题瀑布模式适合：
- 快速分析（1-2 分钟出报告）
- 结构化输出（直接可用）
- 团队分享（完整框架）
- 问题诊断（系统性分析）

## 输出示例（瀑布模式）

```markdown
# 思维树构建师

## 结构化问题分析

### 🎯 核心问题提炼
用户的核心问题是：...
表面看是...，但本质是：...

### 📋 问题范围界定
...

### 🏆 成功目标设定
...

### ⚠️ 风险挑战识别
...

### 💡 解决方案制定
...

### 🔄 行动计划规划
...

## 多维度思维分析

### 🔍 事实依据
...

### 👁️ 多维视角
...

### 🔗 关联分析
...

### 🧠 合理推论
...

### 📊 重要性评估
...
```

## 部署到 Vercel

### 一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/lj22503/problem-tree-tool)

### 手动部署

```bash
npm install -g vercel
vercel login
vercel --prod
```

详细部署指南请查看 [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md)。

## 项目结构

```
problem-tree-tool/
├── app.py                 # 多轮对话模式（v1.0）
├── app_v2.py             # 双模式版本（v2.0）⭐
├── modules/
│   ├── ai_module.py      # AI 集成
│   ├── prompts_waterfall.py  # 瀑布模式提示词
│   └── ...
├── articles/
│   └── problem-tree-tool-article.md  # 公众号文章
├── vercel.json           # Vercel 部署配置
└── VERCEL_DEPLOY.md      # 部署指南
```

## 许可证

MIT

## 致谢

- 基于"全景式问题解决树"框架
- 使用 Streamlit 构建界面
- Claude/OpenAI API 提供 AI 能力

## 链接

- **GitHub**: https://github.com/lj22503/problem-tree-tool
- **在线体验**: https://problem-tree-tool.vercel.app
- **公众号文章**: [我把 2 年的问题拆解方法论，做成了一个 AI 工具](articles/problem-tree-tool-article.md)
- **部署指南**: [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md)
