# 灵光问题树工具

基于全景式问题解决树框架的AI引导问题拆解工具。使用Streamlit构建，支持多AI模型后端。

## 功能特点

- **AI引导问题拆解**: 基于七步闭环流程（问题淬炼、定义、成功标准、挑战评估、方案生成、行动迭代）
- **五大心智透镜**: 证据、视角、联系、猜想、相关
- **两大洞察力标准**: 看得远（回路）、看得透（层级）
- **会话历史管理**: 保存所有问题树会话，支持继续和回顾
- **多种导出格式**: Markdown、JSON，支持PDF转换
- **多AI模型支持**: Claude、OpenAI等

## 安装与运行

### 1. 克隆或下载项目

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置API密钥
复制 `.env.example` 为 `.env` 并填写你的API密钥：
```bash
cp .env.example .env
```
编辑 `.env` 文件，添加你的API密钥。

### 4. 运行应用
```bash
streamlit run app.py
```

## 使用指南

### 新建会话
1. 在"新建会话"页面输入你的初始问题
2. 选择AI模型（需要对应的API密钥）
3. 点击"开始分析"

### 对话流程
1. AI会按照问题解决框架逐步引导
2. 在每个阶段回答AI的提问
3. 对话历史会实时保存

### 导出报告
1. 在"导出报告"页面预览报告
2. 下载Markdown格式的报告
3. 可复制到剪贴板或转换为PDF

### 历史会话
- 查看所有历史会话
- 继续未完成的会话
- 删除不需要的会话

## 项目结构

```
problem_tree_tool/
├── app.py                 # Streamlit主应用
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── .env.production.example # 生产环境配置示例
├── README.md            # 本文件
├── DEPLOYMENT.md        # 详细部署指南
├── Dockerfile           # Docker容器配置
├── docker-compose.yml   # Docker Compose配置
├── runtime.txt          # Python版本指定
├── .streamlit/          # Streamlit配置
│   └── config.toml
├── data/                # 数据存储目录
├── modules/             # 核心模块
│   ├── __init__.py
│   ├── ai_module.py    # AI集成模块
│   ├── models.py       # 数据模型
│   └── utils.py        # 工具函数
├── static/             # 静态资源
├── demo.py             # 演示应用
└── test_basic.py       # 基本功能测试
```

## 配置选项

### AI模型选择
- Claude: `claude-3-5-sonnet`, `claude-3-haiku`
- OpenAI: `gpt-4`, `gpt-3.5-turbo`

### 数据存储
- 会话数据保存在 `data/sessions.json`
- 可配置数据目录路径

## 开发说明

### 添加新的AI后端
1. 在 `ai_module.py` 中继承 `AIBackend` 类
2. 实现 `generate_response` 方法
3. 在 `ProblemTreeAI` 类中添加后端支持

### 自定义提示词
修改 `PromptEngine` 类中的系统提示词和阶段提示词。

## 生产部署

灵光问题树工具支持多种部署方式：

### 快速部署选项
1. **Streamlit Community Cloud** - 最简单的部署方式，免费托管
2. **Hugging Face Spaces** - 支持Streamlit应用，社区友好
3. **Railway.app** - 简单易用的应用部署平台
4. **Docker部署** - 自托管或云服务器部署

详细部署指南请查看 [DEPLOYMENT.md](DEPLOYMENT.md)。

### 部署前准备
- 确保拥有AI API密钥（Claude/OpenAI/DeepSeek）
- 配置环境变量（不要提交敏感信息到代码仓库）
- 测试本地运行正常

## 许可证

MIT

## 致谢

- 基于"全景式问题解决树"框架
- 使用Streamlit构建界面
- Claude/OpenAI API提供AI能力