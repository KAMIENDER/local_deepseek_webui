#!/bin/bash

# 启动Ollama服务
ollama serve &

# 等待Ollama服务启动
sleep 5

# 检查模型是否已存在，如果不存在则下载
if ! ollama list | grep -q "deepseek-r1:7b"; then
    echo "正在下载 deepseek-r1:7b 模型..."
    ollama pull deepseek-r1:7b
else
    echo "deepseek-r1:7b 模型已存在，跳过下载"
fi

# 启动FastAPI服务
python -m uvicorn api:app --host 0.0.0.0 --port 8000 &

# 启动Streamlit服务
streamlit run webui.py --server.port 8501 --server.address 0.0.0.0

# 等待所有后台进程
wait