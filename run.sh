#!/bin/bash

echo "============================================"
echo "灵光问题树工具 - 启动脚本"
echo "============================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python 3。请先安装Python 3.8+。"
    exit 1
fi

# 检查依赖
echo "检查依赖包..."
python3 -c "import streamlit, json, datetime, os" &> /dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 安装依赖包失败。"
        exit 1
    fi
fi

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件。"
    echo "正在创建.env.example的副本..."
    cp .env.example .env
    echo ""
    echo "请编辑.env文件，添加你的API密钥："
    echo "1. ANTHROPIC_API_KEY (Claude API)"
    echo "2. OPENAI_API_KEY (OpenAI API)"
    echo ""
    read -p "按回车键继续..." </dev/tty
fi

# 运行应用
echo "启动灵光问题树工具..."
echo ""
echo "应用将在浏览器中打开：http://localhost:8501"
echo "按 Ctrl+C 停止应用"
echo ""
echo "============================================"

streamlit run app.py