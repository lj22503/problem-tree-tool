# Vercel 部署指南

## 快速部署（推荐）

### 方式一：一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/lj22503/problem-tree-tool)

点击按钮，按提示操作：
1. 选择 GitHub 仓库
2. 配置环境变量（API 密钥）
3. 点击 Deploy

### 方式二：手动部署

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录 Vercel
vercel login

# 3. 部署
cd problem-tree-tool
vercel --prod
```

## 环境变量配置

在 Vercel Dashboard → Settings → Environment Variables 添加：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | Claude API 密钥 | `sk-ant-...` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-...` |

**注意**：不要提交 `.env` 文件到 Git！

## 使用说明

### 用户访问

部署成功后，用户访问：
- **开发环境**: `https://problem-tree-tool-xxx.vercel.app`
- **生产环境**: `https://problem-tree-tool.vercel.app`（需绑定域名）

### 两种模式

1. **💬 多轮对话模式**
   - 输入问题
   - AI 逐步引导（7 步）
   - 导出 Markdown 报告

2. **🌊 问题瀑布模式**
   - 输入问题
   - 一键生成完整框架
   - 直接下载/复制

## 成本估算

- **Vercel 免费版**: 每月 100GB 带宽，足够个人使用
- **API 费用**: 按使用量计算（Claude/OpenAI）
  - 单次分析：~$0.01-0.05
  - 每月 1000 次：~$10-50

## 自定义域名（可选）

1. Vercel Dashboard → Settings → Domains
2. 添加域名：`problem-tree.yourdomain.com`
3. 配置 DNS：
   ```
   CNAME cname.vercel-dns.com
   ```

## 故障排查

### 问题 1: 部署失败
- 检查 `requirements.txt` 格式
- 检查 `vercel.json` 配置
- 查看部署日志

### 问题 2: API 调用失败
- 检查环境变量是否配置
- 检查 API 密钥是否有效
- 查看 API 额度是否充足

### 问题 3: Streamlit 加载慢
- Streamlit 在 Vercel 上是冷启动
- 首次加载可能需要 10-30 秒
- 后续访问会快很多

---

**部署完成检查清单**：
- [ ] 网页可访问
- [ ] 两种模式都能用
- [ ] API 调用正常
- [ ] 导出功能正常
- [ ] 移动端适配正常
