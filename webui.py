import streamlit as st
import requests
import json
import time

# 设置页面标题和布局
st.set_page_config(page_title="LLM Chat Interface", layout="wide")
st.title("💬 LLM Chat Interface")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 侧边栏配置
with st.sidebar:
    st.header("模型配置")
    
    # 获取可用模型列表
    try:
        response = requests.get("http://localhost:8000/models")
        if response.status_code == 200:
            models_data = response.json()
            if "models" in models_data:
                models = [model["name"] for model in models_data["models"]]
            else:
                models = ["deepseek-coder:7b-instruct-q4_0"]
        else:
            models = ["无可用模型"]
    except Exception as e:
        st.error(f"获取模型列表失败: {str(e)}")
        models = ["服务器连接失败"]
    
    # 模型选择和参数配置
    selected_model = st.selectbox("选择模型", models)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    system_prompt = st.text_area("System Prompt", height=100)
    
    # 添加模型下载功能
    st.header("下载新模型")
    new_model = st.text_input("模型名称", placeholder="例如: deepseek-coder:7b-instruct-q4_0")
    if st.button("下载模型"):
        if new_model:
            try:
                # 开始下载
                response = requests.post(f"http://localhost:8000/models/download/{new_model}")
                if response.status_code == 200:
                    st.success("开始下载模型，请等待...")
                    
                    # 创建进度条
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 轮询下载状态
                    while True:
                        status_response = requests.get(f"http://localhost:8000/models/download/{new_model}/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if status_data["status"] == "downloading":
                                progress = status_data["progress"]
                                progress_bar.progress(progress / 100)
                                status_text.text(f"下载进度: {progress}%")
                            elif status_data["status"] == "completed":
                                progress_bar.progress(100)
                                status_text.text("下载完成！")
                                st.success("模型下载成功，请刷新页面以使用新模型。")
                                break
                            elif status_data["status"] == "failed":
                                st.error(f"下载失败: {status_data.get('error', '未知错误')}")
                                break
                        time.sleep(1)
                else:
                    st.error("下载请求失败")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
        else:
            st.warning("请输入模型名称")

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("输入你的问题"):
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 调用API获取响应
    with st.chat_message("assistant"):
        with st.spinner("思考中..."): 
            try:
                # 构建消息数组
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                # 创建响应占位符
                response_placeholder = st.empty()
                thought_expander = st.expander("查看思考过程", expanded=False)
                full_response = ""
                thought_extracted = False
                
                # 使用SSE接收流式响应
                with requests.post(
                    "http://localhost:8000/chat",
                    json={
                        "model": selected_model,
                        "messages": messages,
                        "temperature": temperature,
                        "stream": True
                    },
                    stream=True
                ) as response:
                    if response.status_code == 200:
                        for line in response.iter_lines():
                            if line:
                                line = line.decode('utf-8')
                                if line.startswith('data: '):
                                    try:
                                        data = json.loads(line[6:])
                                        if 'error' in data:
                                            st.error(f"发生错误: {data['error']}")
                                            break
                                        content = data['content']
                                        full_response += content
                                        
                                        # 检查是否包含完整的思考过程
                                        if not thought_extracted and "<think>" in full_response and "</think>" in full_response:
                                            parts = full_response.split("</think>")
                                            thought = parts[0].split("<think>")[1].strip()
                                            answer = parts[1].strip()
                                            
                                            # 只显示一次思考过程
                                            if thought:
                                                with thought_expander:
                                                    st.markdown(thought)
                                            thought_extracted = True
                                            full_response = answer
                                            
                                        # 更新主要回答
                                        response_placeholder.markdown(full_response)
                                    except json.JSONDecodeError:
                                        continue
                    else:
                        st.error(f"请求失败: {response.text}")
                
                # 将完整响应添加到会话历史
                # 如果响应中包含思考过程，只保存实际回答部分
                if "<think>" in full_response and "</think>" in full_response:
                    parts = full_response.split("</think>")
                    answer = parts[1].strip()
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"发生错误: {str(e)}")