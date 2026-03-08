# 灵光问题树工具 - 演示模式使用指南

## 问题现象
在Windows环境下运行Streamlit时，会遇到交互式提示要求输入邮箱，这可能导致进程阻塞。

## 解决方案（三种方法）

### 方法1: 直接运行（最简单）
1. 打开终端（CMD或PowerShell）
2. 导航到项目目录：
   ```bash
   cd "C:\Users\lj225\Documents\Obsidian Vault\problem_tree_tool"
   ```
3. 运行演示模式：
   ```bash
   python -m streamlit run demo.py
   ```
4. **关键步骤**: 当出现以下提示时：
   ```
   Welcome to Streamlit!

   If you'd like to receive helpful onboarding emails...
   Email:
   ```
   **直接按Enter键（不要输入任何内容）**
5. 等待应用启动，然后在浏览器访问：http://localhost:8501

### 方法2: 使用批处理文件（推荐）
1. 双击 `run.bat`
2. 按提示操作（会跳过Streamlit的交互提示）

### 方法3: 手动配置环境变量
1. 在终端中运行：
   ```bash
   set STREAMLIT_GLOBAL_DEVELOPMENT_MODE=1
   set STREAMLIT_GLOBAL_SHOW_WARNING_ON_DIRECT_EXECUTION=0
   python -m streamlit run demo.py
   ```

## 演示内容预览

即使无法启动Web界面，你也可以通过以下方式了解工具功能：

### 1. 查看核心框架
工具基于"全景式问题解决树"框架：
- **七步闭环流程**: 问题淬炼 → 定义 → 成功标准 → 挑战评估 → 方案生成 → 行动迭代
- **五大心智透镜**: 证据、视角、联系、猜想、相关
- **两大洞察标准**: 回路（看得远）、层级（看得透）

### 2. 查看代码结构
```
problem_tree_tool/
├── app.py                    # 主应用（需要API密钥）
├── demo.py                   # 演示应用（无需API密钥）
├── modules/                  # 核心模块
│   ├── ai_module.py         # AI集成和提示词管理
│   ├── models.py            # 数据模型（会话、消息等）
│   └── utils.py             # 工具函数
└── data/                    # 数据存储目录
```

### 3. 运行基本测试
```bash
python test_basic.py
```
这会验证所有核心功能是否正常工作。

## 完整版本运行

要运行完整版本（需要AI API密钥）：

1. 复制配置文件：
   ```bash
   copy .env.example .env
   ```

2. 编辑 `.env` 文件，添加API密钥：
   ```
   ANTHROPIC_API_KEY=your_claude_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

3. 运行主应用：
   ```bash
   python -m streamlit run app.py
   ```
   同样，出现邮箱提示时直接按Enter。

## 常见问题

### Q1: 应用启动后无法访问 http://localhost:8501
- 检查端口是否被占用（尝试 http://localhost:8502）
- 等待Streamlit完全启动（可能需要10-20秒）
- 查看终端输出是否有错误信息

### Q2: 想停止应用
- 在运行Streamlit的终端中按 `Ctrl+C`

### Q3: 想查看演示内容但不启动Web服务器
- 直接阅读 `demo.py` 文件，查看演示数据和界面代码
- 查看 `README.md` 了解完整功能说明

### Q4: 如何自定义提示词？
- 编辑 `modules/ai_module.py` 中的 `PromptEngine` 类
- 修改系统提示词和阶段提示词

## 技术支持

如果以上方法都无法解决问题，可以：
1. 查看Streamlit官方文档
2. 检查Python和Streamlit版本
3. 尝试在其他环境（如Linux子系统）中运行

---
**项目状态**: 所有代码已通过基本功能测试
**最后更新**: 2026-03-08
**框架完整性**: 100% 实现"全景式问题解决树"框架