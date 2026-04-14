# Vercel 部署指南

## 快速部署（5 分钟）

### 步骤 1: 准备代码

```bash
cd problem-tree-tool

# 确认文件齐全
ls -la
# 应该看到：
# - app_v2.py (优化版主应用)
# - vercel.json (Vercel 配置)
# - requirements.txt (依赖)
# - runtime.txt (Python 版本)
```

### 步骤 2: 推送到 GitHub

```bash
# 初始化 Git（如果还没有）
git init
git add .
git commit -m "feat: 优化版 + Vercel 部署配置"

# 创建 GitHub 仓库并推送
git branch -M main
git remote add origin https://github.com/你的用户名/problem-tree-tool.git
git push -u origin main
```

### 步骤 3: 部署到 Vercel

1. **访问 Vercel**
   - 打开 https://vercel.com
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 "Add New Project"
   - 选择 "Import Git Repository"
   - 选择你的 `problem-tree-tool` 仓库

3. **配置环境变量**
   在 Vercel 项目设置 → Environment Variables 中添加：
   ```
   DEEPSEEK_API_KEY=sk-your-deepseek-key
   ANTHROPIC_API_KEY=sk-ant-your-key (可选)
   OPENAI_API_KEY=sk-your-key (可选)
   ```

4. **部署**
   - 点击 "Deploy"
   - 等待 2-3 分钟
   - 部署成功后会获得一个 URL：`https://problem-tree-tool-xxx.vercel.app`

### 步骤 4: 测试访问

打开 Vercel 提供的 URL，测试：
- ✅ 新建会话
- ✅ 问题拆解
- ✅ 导出报告

---

## 本地测试 Vercel 配置

### 安装 Vercel CLI

```bash
npm install -g vercel
```

### 本地运行

```bash
# 登录 Vercel
vercel login

# 链接项目
vercel link

# 本地开发
vercel dev
```

访问 `http://localhost:3000` 测试

---

## 环境变量说明

| 变量名 | 必需 | 说明 | 获取方式 |
|--------|------|------|---------|
| `DEEPSEEK_API_KEY` | 推荐 | DeepSeek API 密钥 | https://platform.deepseek.com |
| `ANTHROPIC_API_KEY` | 可选 | Claude API 密钥 | https://console.anthropic.com |
| `OPENAI_API_KEY` | 可选 | OpenAI API 密钥 | https://platform.openai.com |
| `DEBUG` | 否 | 调试模式 | `False` (生产环境) |
| `DATA_DIR` | 否 | 数据目录 | `./data` |

---

## 自定义域名（可选）

1. **Vercel 项目设置**
   - Settings → Domains
   - 添加你的域名：`problem-tree.yourdomain.com`

2. **DNS 配置**
   - 添加 CNAME 记录指向 `cname.vercel-dns.com`

3. **HTTPS**
   - Vercel 自动配置 SSL 证书

---

## 性能优化

### 1. 启用缓存

Vercel 自动缓存静态资源，无需额外配置。

### 2. 环境变量优化

将 API 密钥配置在 Vercel 环境变量中，不要提交到代码仓库。

### 3. 构建优化

```json
// vercel.json
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": ".streamlit"
}
```

---

## 故障排除

### 问题 1: 部署失败

**错误**: `ModuleNotFoundError: No module named 'streamlit'`

**解决**:
```bash
# 确认 requirements.txt 存在
cat requirements.txt

# 重新推送
git add requirements.txt
git commit -m "fix: add requirements.txt"
git push
```

### 问题 2: API 密钥错误

**错误**: `ValueError: 未提供 API 密钥`

**解决**:
- 检查 Vercel 环境变量是否配置
- 确认密钥格式正确
- 重启 Vercel 部署

### 问题 3: 数据丢失

**问题**: Vercel 是无服务器部署，重启后数据丢失

**解决**:
- 使用外部数据库（Vercel Postgres）
- 或导出报告到本地

---

## 部署检查清单

- [ ] 代码推送到 GitHub
- [ ] Vercel 项目创建
- [ ] 环境变量配置
- [ ] 部署成功
- [ ] 访问测试通过
- [ ] 新建会话测试
- [ ] 问题拆解测试
- [ ] 导出报告测试
- [ ] 移动端适配测试

---

## 后续优化

1. **添加用户系统**: Clerk / NextAuth
2. **会话持久化**: Vercel Postgres
3. **付费功能**: Stripe 集成
4. **数据分析**: Vercel Analytics

---

**部署时间**: 5-10 分钟  
**难度**: ⭐⭐☆☆☆ (简单)  
**成本**: $0 (Vercel 免费套餐)
