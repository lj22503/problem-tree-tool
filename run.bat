@echo off
echo ============================================
echo 灵光问题树工具 - 启动脚本
echo ============================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python。请先安装Python 3.8+。
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖包...
python -c "import streamlit, json, datetime, os" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 安装依赖包失败。
        pause
        exit /b 1
    )
)

REM 检查环境变量
if not exist ".env" (
    echo 警告: 未找到.env文件。
    echo 正在创建.env.example的副本...
    copy .env.example .env
    echo.
    echo 请编辑.env文件，添加你的API密钥：
    echo 1. ANTHROPIC_API_KEY (Claude API)
    echo 2. OPENAI_API_KEY (OpenAI API)
    echo.
    pause
)

REM 运行应用
echo 启动灵光问题树工具...
echo.
echo 应用将在浏览器中打开：http://localhost:8501
echo 按 Ctrl+C 停止应用
echo.
echo ============================================

streamlit run app.py