FROM python:3.11-slim

# 安装基本依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# 设置工作目录
WORKDIR /app

# 设置工作目录为挂载点
VOLUME /app

# 复制所有必要文件
COPY . /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r /app/requirements.txt

# 创建数据目录
RUN mkdir -p /app/data

# 设置start.sh权限
RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 8000
EXPOSE 8501
EXPOSE 11434

# 启动服务
CMD ["/app/start.sh"]