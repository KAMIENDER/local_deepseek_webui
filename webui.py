import streamlit as st
import requests
import json
import time
from i18n import LANGUAGES

# 获取当前语言的文本


def get_text(key):
    return LANGUAGES[st.session_state.language][key]

# 初始化语言设置
if "language" not in st.session_state:
    st.session_state.language = "zh"

# 初始化会话状态
if "chats" not in st.session_state:
    st.session_state.chats = [{
        "id": 0,
        "name": get_text("chat_name").format(1),
        "messages": [],
        "model": "deepseek-r1:7b",
        "temperature": 0.7,
        "system_prompt": ""
    }]

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = 0

# 设置页面标题和布局
st.set_page_config(page_title="LLM Chat Interface", layout="wide")


# 引用外部CSS文件
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 侧边栏配置
with st.sidebar:
    # 语言选择下拉框
    st.session_state.language = st.selectbox(
        "🌐 Language/语言",
        ["zh", "en"],
        format_func=lambda x: "中文" if x == "zh" else "English",
        index=0 if st.session_state.language == "zh" else 1
    )

    # 新建会话按钮
    if st.button(get_text("new_chat")):
        new_chat_id = len(st.session_state.chats)
        st.session_state.chats.append({
            "id": new_chat_id,
            "name": get_text("chat_name").format(new_chat_id + 1),
            "messages": [],
            "model": st.session_state.chats[st.session_state.current_chat_id]["model"],
            "temperature": st.session_state.chats[st.session_state.current_chat_id]["temperature"],
            "system_prompt": st.session_state.chats[st.session_state.current_chat_id]["system_prompt"]
        })
        st.session_state.current_chat_id = new_chat_id

    # 会话列表
    st.header(get_text("chat_list"))
    for chat in st.session_state.chats:
        col1, col2 = st.columns([8, 2])
        with col1:
            # 使用可编辑的div实现单击切换和双击编辑
            if f"editing_chat_{chat['id']}" not in st.session_state:
                st.session_state[f"editing_chat_{chat['id']}"] = False

            if st.session_state[f"editing_chat_{chat['id']}"]:
                new_name = st.text_input(
                    "",
                    value=chat["name"],
                    key=f"chat_name_{chat['id']}",
                    label_visibility="collapsed",
                    on_change=lambda chat_id=chat['id']: setattr(
                        st.session_state.chats[chat_id], 'name', st.session_state[f"chat_name_{chat_id}"])
                )
                # 按回车或失去焦点时退出编辑模式
                st.session_state[f"editing_chat_{chat['id']}"] = False
            else:  # 显示模式
                # 创建一个可点击的div来处理单击和双击事件
                chat_div = st.empty()
                chat_div.markdown(
                    f'<div class="chat-name" id="chat_{chat["id"]}">{chat["name"]}</div>', unsafe_allow_html=True)

                # 添加JavaScript处理单击和双击事件
                st.markdown(f"""
                    <script>
                        document.getElementById('chat_{chat["id"]}').addEventListener('click', function(e) {{
                            const now = Date.now();
                            const lastClick = this.getAttribute('data-last-click') || 0;
                            
                            if (now - lastClick < 300) {{ // 双击
                                window.Streamlit.setComponentValue('editing_chat_{chat["id"]}', true);
                            }} else {{ // 单击
                                window.Streamlit.setComponentValue('current_chat_id', {chat["id"]});
                            }}
                            
                            this.setAttribute('data-last-click', now);
                        }});
                    </script>
                """, unsafe_allow_html=True)
        with col2:
            if len(st.session_state.chats) > 1 and st.button("🗑️", key=f"delete_{chat['id']}"):
                if st.button(get_text("confirm_delete"), key=f"confirm_delete_{chat['id']}"):
                    st.session_state.chats.remove(chat)
                    if st.session_state.current_chat_id == chat["id"]:
                        st.session_state.current_chat_id = 0

# 主界面
st.title(get_text("title"))

# 设置菜单
with st.expander("⚙️ " + get_text("settings")):
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
    
    current_chat = st.session_state.chats[st.session_state.current_chat_id]

    # 模型选择和参数配置
    current_chat["model"] = st.selectbox(
        get_text("select_model"), models, index=models.index(current_chat["model"]))
    current_chat["temperature"] = st.slider(
        "Temperature", min_value=0.0, max_value=1.0, value=current_chat["temperature"], step=0.1)
    current_chat["system_prompt"] = st.text_area(
        get_text("system_prompt"), current_chat["system_prompt"], height=100)
    
    # 添加模型下载功能
    st.header(get_text("download_model"))
    new_model = st.text_input(get_text("model_name"),
                              placeholder=get_text("model_placeholder"))
    if st.button(get_text("download_button")):
        if new_model:
            try:
                response = requests.post(f"http://localhost:8000/models/download/{new_model}")
                if response.status_code == 200:
                    st.success(get_text("download_start"))
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    while True:
                        status_response = requests.get(f"http://localhost:8000/models/download/{new_model}/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data["status"]
                            progress = status_data.get("progress", 0)

                            if status == "downloading":
                                progress_bar.progress(progress / 100)
                                status_text.text(
                                    get_text("download_progress").format(progress))
                            elif status == "verifying":
                                progress_bar.progress(0.99)
                                status_text.text(get_text("verifying_model"))
                            elif status == "writing":
                                progress_bar.progress(0.99)
                                status_text.text(get_text("writing_model"))
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

# 显示当前会话的聊天历史
current_chat = st.session_state.chats[st.session_state.current_chat_id]
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        if "thought" in message and message["thought"]:
            with st.expander(get_text("view_thoughts"), expanded=False):
                st.markdown(message["thought"])
        st.markdown(message["content"])

# 创建固定在底部的输入区域
chat_input = st.chat_input(get_text("input_placeholder"))

if chat_input:
    # 添加用户消息到历史
    current_chat["messages"].append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.markdown(chat_input)
    
    # 调用API获取响应
    with st.chat_message("assistant"):
        with st.spinner(get_text("thinking")):
            try:
                # 构建消息数组
                messages = []
                if current_chat["system_prompt"]:
                    messages.append(
                        {"role": "system", "content": current_chat["system_prompt"]})
                messages.extend(current_chat["messages"])
                
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
                        "model": current_chat["model"],
                        "messages": messages,
                        "temperature": current_chat["temperature"],
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

                                        if not thought_extracted and "<think>" in full_response and "</think>" in full_response:
                                            parts = full_response.split("</think>")
                                            thought = parts[0].split("<think>")[1].strip()
                                            answer = parts[1].strip()

                                            if thought:
                                                with thought_expander:
                                                    st.markdown(thought)
                                            thought_extracted = True
                                            full_response = answer

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
                    current_chat["messages"].append({
                        "role": "assistant",
                        "content": answer
                    })
                else:
                    current_chat["messages"].append({
                        "role": "assistant",
                        "content": full_response
                    })
            except Exception as e:
                st.error(get_text("error_occurred").format(str(e)))
