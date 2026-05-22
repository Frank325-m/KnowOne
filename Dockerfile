# RAG 知识库问答系统 Dockerfile
# 多阶段构建以减小镜像大小

# 第一阶段：构建阶段
FROM python:3.11-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 创建非 root 用户
RUN groupadd -r raguser && useradd -r -g raguser raguser

# 创建必要的目录
RUN mkdir -p /app/docs /app/resource /app/logs /app/model_cache \
    && chown -R raguser:raguser /app

# 从构建阶段复制已安装的 Python 包
COPY --from=builder /root/.local /root/.local

# 确保 Python 可以找到用户安装的包
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY . .

# 设置文件权限
RUN chown -R raguser:raguser /app

# 切换到非 root 用户
USER raguser

# 暴露端口
EXPOSE 7801

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7801/', timeout=5)" || exit 1

# 设置默认命令
CMD ["python", "web_rag_app.py"]