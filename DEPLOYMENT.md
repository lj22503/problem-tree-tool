# 灵光问题树工具 - 生产部署指南

本文档介绍如何将灵光问题树工具部署到生产环境，让其他人可以通过互联网使用。

## 部署前准备

### 1. 确保代码准备就绪
- 项目根目录包含 `app.py`（主应用入口）
- `requirements.txt` 包含所有依赖
- `.streamlit/config.toml` 包含Streamlit配置
- `runtime.txt` 指定Python版本（可选，推荐）

### 2. 准备API密钥
工具需要AI API密钥才能正常工作，你需要准备：
- **Anthropic Claude API密钥**（用于Claude模型）
- **OpenAI API密钥**（用于GPT模型）
- **DeepSeek API密钥**（可选，用于DeepSeek模型）

## 部署选项

### 选项1: Streamlit Community Cloud（推荐）

Streamlit Community Cloud是最简单的部署方式，提供免费托管服务。

#### 部署步骤：

1. **注册账号**
   - 访问 [Streamlit Community Cloud](https://streamlit.io/cloud)
   - 使用GitHub账号登录

2. **推送代码到GitHub**
   - 在GitHub创建新仓库
   - 将本地代码推送到GitHub：
     ```bash
     git init
     git add .
     git commit -m "Initial commit"
     git branch -M main
     git remote add origin https://github.com/你的用户名/仓库名.git
     git push -u origin main
     ```

3. **部署到Streamlit Cloud**
   - 登录 [Streamlit Cloud](https://share.streamlit.io/)
   - 点击 "New app"
   - 选择你的GitHub仓库、分支和主文件路径（`app.py`）
   - 配置环境变量（见下文）

4. **配置环境变量**
   在Streamlit Cloud的设置页面，添加以下环境变量：
   ```
   ANTHROPIC_API_KEY = 你的Claude API密钥
   OPENAI_API_KEY = 你的OpenAI API密钥
   DEBUG = False
   DATA_DIR = ./data
   ```

5. **部署并访问**
   - 点击 "Deploy"，等待部署完成
   - 应用将有一个公开的URL，如 `https://app名-用户名.streamlit.app`

#### Streamlit Cloud注意事项：
- 免费套餐有使用限制
- 数据存储在临时文件系统中（重启应用可能丢失数据）
- 支持自定义域名（付费功能）

### 选项2: Hugging Face Spaces

Hugging Face Spaces也支持Streamlit应用部署，提供免费托管。

#### 部署步骤：

1. **注册账号**
   - 访问 [Hugging Face](https://huggingface.co)
   - 创建账号并登录

2. **创建新的Space**
   - 点击右上角用户头像 → "New Space"
   - 填写Space名称
   - SDK选择 "Streamlit"
   - 选择可见性（Public或Private）

3. **上传代码**
   - 可以通过Git推送代码：
     ```bash
     git clone https://huggingface.co/spaces/你的用户名/space名
     cd space名
     # 复制项目文件到目录
     git add .
     git commit -m "Add app"
     git push
     ```
   - 或通过Web界面上传文件

4. **配置环境变量**
   - 在Space的"Settings" → "Repository secrets"中添加：
     - `ANTHROPIC_API_KEY`
     - `OPENAI_API_KEY`

5. **访问应用**
   - 应用将运行在：`https://huggingface.co/spaces/你的用户名/space名`

#### Hugging Face Spaces特点：
- 免费提供CPU资源
- 支持Git版本控制
- 社区友好，易于分享

### 选项3: Railway.app

Railway提供简单易用的应用部署平台。

#### 部署步骤：

1. **注册账号**
   - 访问 [Railway](https://railway.app)
   - 使用GitHub账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"

3. **配置环境变量**
   - 在项目的"Variables"标签页添加所需环境变量

4. **配置部署设置**
   - Railway会自动检测Python项目
   - 如果需要，可以添加 `requirements.txt` 和 `runtime.txt`

5. **访问应用**
   - Railway会自动分配一个公开URL

### 选项4: 自托管（Docker部署）

如果你有自己的服务器，可以使用Docker部署。

#### Docker部署步骤：

1. **创建Dockerfile**
   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **构建和运行**
   ```bash
   # 构建镜像
   docker build -t problem-tree-tool .

   # 运行容器
   docker run -d \
     -p 8501:8501 \
     -e ANTHROPIC_API_KEY=你的密钥 \
     -e OPENAI_API_KEY=你的密钥 \
     -e DEBUG=False \
     --name problem-tree \
     problem-tree-tool
   ```

3. **使用Docker Compose（推荐）**
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8501:8501"
       environment:
         - ANTHROPIC_API_KEY=你的密钥
         - OPENAI_API_KEY=你的密钥
         - DEBUG=False
       volumes:
         - ./data:/app/data
       restart: unless-stopped
   ```

## 环境变量配置

所有部署方式都需要配置以下环境变量：

| 变量名 | 说明 | 必需 | 示例 |
|--------|------|------|------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API密钥 | 是（如使用Claude） | `sk-ant-...` |
| `OPENAI_API_KEY` | OpenAI API密钥 | 是（如使用GPT） | `sk-...` |
| `DEBUG` | 调试模式 | 否 | `False`（生产环境） |
| `DATA_DIR` | 数据存储目录 | 否 | `./data` |

## 生产环境建议

### 安全性
1. **API密钥管理**：不要将API密钥提交到代码仓库
2. **HTTPS**：确保应用使用HTTPS
3. **访问限制**：考虑添加身份验证（Streamlit有内置支持）

### 性能优化
1. **缓存**：Streamlit支持`@st.cache_data`和`@st.cache_resource`
2. **会话管理**：定期清理旧会话数据
3. **资源监控**：监控应用内存和CPU使用

### 数据持久化
当前版本使用本地文件系统存储数据，在云部署中：
- Streamlit Cloud：数据可能在应用重启后丢失
- 考虑使用数据库（SQLite、PostgreSQL）或云存储（S3）进行持久化

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查 `requirements.txt` 是否正确
   - 确认Python版本兼容（3.8+）
   - 查看部署日志

2. **AI功能不工作**
   - 确认API密钥已正确设置
   - 检查API密钥是否有余额或权限
   - 查看网络连接（某些地区可能需要代理）

3. **数据丢失**
   - 云平台文件系统可能是临时的
   - 考虑实现数据持久化方案

4. **性能问题**
   - 减少每个会话的消息数量
   - 增加缓存使用
   - 考虑升级部署套餐

## 更新和维护

1. **代码更新**：推送新代码到Git仓库，部署平台会自动重新部署
2. **依赖更新**：更新 `requirements.txt` 并重新部署
3. **监控日志**：定期检查应用日志，及时发现和解决问题

## 支持与帮助

- 查看项目 [README.md](README.md) 了解基本使用
- 查阅 [DEMO_GUIDE.md](DEMO_GUIDE.md) 了解演示模式
- 在GitHub Issues中报告问题

---

**最后更新**: 2026-03-08
**部署状态**: 所有代码已通过基本测试，适合生产部署