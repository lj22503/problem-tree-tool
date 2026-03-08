# 灵光问题树工具 - Docker镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（如果需要）
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量默认值
ENV DEBUG=False
ENV DATA_DIR=./data
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHERUSAGESTATS=false

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# 运行Streamlit应用
CMD ["streamlit", "run", "app.py", \
    "--server.port=${STREAMLIT_SERVER_PORT}", \
    "--server.address=${STREAMLIT_SERVER_ADDRESS}", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=${STREAMLIT_BROWSER_GATHERUSAGESTATS}"]