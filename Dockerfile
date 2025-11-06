FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖（适配 Debian slim / Ubuntu 24 主机环境）
ARG DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
    apt-get update -o Acquire::Retries=3 --fix-missing; \
    apt-get install -y --no-install-recommends \
      build-essential gcc g++ \
      libpq-dev \
      libgomp1 \
      libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 \
      tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim \
    ; \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 创建必要的目录
RUN mkdir -p /app/logs /app/uploads /app/temp

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 默认命令
CMD ["python", "app/main.py"]

