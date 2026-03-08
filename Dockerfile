# 多阶段构建：优化镜像大小

# ==================== 阶段1：构建 ====================
FROM python:3.12-slim as builder

# 设置工作目录
WORKDIR /build

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 创建appuser（如果不存在）
RUN useradd -m -u 1000 appuser 2>/dev/null || echo "appuser already exists"

# 复制依赖文件
COPY requirements.txt .

# 以appuser安装Python依赖
RUN chown -R appuser:appuser /build && \
    su -s /bin/bash -c "pip install --no-cache-dir --user -r requirements.txt" appuser

# ==================== 阶段2：运行时镜像 ====================
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 创建appuser
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# 从构建阶段复制Python包
COPY --from=builder /home/appuser/.local /root/.local

# 复制应用代码
COPY --chown=appuser:appuser . .

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf8

# 暴露端口
EXPOSE 8000

# 启动命令（以root用户运行，然后切换到appuser）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 切换到非root用户（在容器启动后执行）
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
