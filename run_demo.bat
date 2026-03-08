@echo off
echo ============================================
echo 灵光问题树工具 - 演示模式启动脚本
echo ============================================
echo.
echo 演示模式无需API密钥，展示工具所有功能界面
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

REM 设置环境变量以跳过Streamlit交互提示
set STREAMLIT_GLOBAL_DEVELOPMENT_MODE=1
set STREAMLIT_GLOBAL_SHOW_WARNING_ON_DIRECT_EXECUTION=0
set STREAMLIT_GLOBAL_SHOW_TUTORIALS=false

REM 运行演示应用
echo 启动演示模式...
echo.
echo 重要: 如果出现邮箱输入提示，请直接按回车键跳过
echo.
echo 应用将在浏览器中打开：http://localhost:8501
echo 按 Ctrl+C 停止应用
echo.
echo ============================================
echo.

REM 运行演示模式，添加参数跳过部分交互
python -m streamlit run demo.py --global.developmentMode false --browser.gatherUsageStats false