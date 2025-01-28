import streamlit as st
import requests
import json
import time
from i18n import LANGUAGES

# 初始化语言设置
if "language" not in st.session_state:
    st.session_state.language = "zh"

# 设置页面标题和布局
st.set_page_config(page_title="LLM Chat Interface", layout="wide")

# 获取当前语言的文本


def get_text(key):
    return LANGUAGES[st.session_state.language][key]


# 侧边栏配置
with st.sidebar:
    # 语言选择下拉框
    st.session_state.language = st.selectbox(
        "🌐 Language/语言",
        ["zh", "en"],
        format_func=lambda x: "中文" if x == "zh" else "English",
        index=0 if st.session_state.language == "zh" else 1
    )

    st.header(get_text("model_config"))

st.title(get_text("title"))

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 引用外部CSS文件
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 侧边栏配置
with st.sidebar:
    st.header(get_text("model_config"))
    
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
            models = [get_text("no_models")]
    except Exception as e:
        st.error(get_text("get_models_error").format(str(e)))
        models = [get_text("server_error")]
    
    # 模型选择和参数配置
    selected_model = st.selectbox(get_text("select_model"), models)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    system_prompt = st.text_area(get_text("system_prompt"), height=100)
    
    # 添加模型下载功能
    st.header(get_text("download_model"))
    new_model = st.text_input(get_text("model_name"),
                              placeholder=get_text("model_placeholder"))
    if st.button(get_text("download_button")):
        if new_model:
            try:
                # 开始下载
                response = requests.post(f"http://localhost:8000/models/download/{new_model}")
                if response.status_code == 200:
                    st.success(get_text("download_start"))
                    
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
                                status_text.text(
                                    get_text("download_progress").format(progress))
                            elif status_data["status"] == "completed":
                                progress_bar.progress(100)
                                status_text.text(get_text("download_complete"))
                                st.success(get_text("download_success"))
                                break
                            elif status_data["status"] == "failed":
                                st.error(get_text("download_failed").format(
                                    status_data.get("error", "未知错误")))
                                break
                        time.sleep(1)
                else:
                    st.error(get_text("request_failed").format(response.text))
            except Exception as e:
                st.error(get_text("error_occurred").format(str(e)))
        else:
            st.warning(get_text("enter_model_name"))

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 创建固定在底部的输入区域
chat_input = st.chat_input(get_text("input_placeholder"))

if chat_input:
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.markdown(chat_input)
    
    # 调用API获取响应
    with st.chat_message("assistant"):
        with st.spinner(get_text("thinking")):
            try:
                # 构建消息数组
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": chat_input})
                
                # 创建响应占位符
                response_placeholder = st.empty()
                thought_expander = st.expander(
                    get_text("view_thoughts"), expanded=False)
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
                                            st.error(
                                                get_text("error_occurred").format(data['error']))
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
                        st.error(
                            get_text("request_failed").format(response.text))
                
                # 将完整响应添加到会话历史
                if "<think>" in full_response and "</think>" in full_response:
                    parts = full_response.split("</think>")
                    answer = parts[1].strip()
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(get_text("error_occurred").format(str(e)))
