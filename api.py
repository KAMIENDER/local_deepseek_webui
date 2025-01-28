from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import ollama
import subprocess
import threading
import time
import json
import requests
from search import WebSearch

app = FastAPI()

# 用于存储下载状态的字典
download_status = {}

def download_model(model_name: str):
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        download_status[model_name] = {"status": "downloading", "progress": 0}
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if "downloading" in output.lower():
                    try:
                        progress = int(output.split('%')[0].split()[-1])
                        download_status[model_name] = {"status": "downloading", "progress": progress}
                    except:
                        pass
        
        if process.returncode == 0:
            download_status[model_name] = {"status": "completed", "progress": 100}
        else:
            error = process.stderr.read()
            download_status[model_name] = {"status": "failed", "error": error}
            
    except Exception as e:
        download_status[model_name] = {"status": "failed", "error": str(e)}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: float = 0.7
    stream: bool = False

class ChatResponse(BaseModel):
    response: str


class SearchRequest(BaseModel):
    query: str
    num_results: int = 5


@app.post("/search")
async def search(request: SearchRequest):
    try:
        results = WebSearch.search_duckduckgo(
            request.query, request.num_results)
        return {"results": [{"title": r.title, "snippet": r.snippet, "link": r.link} for r in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if request.stream:
            # 流式响应
            async def generate():
                try:
                    stream = ollama.chat(
                        model=request.model,
                        messages=[msg.dict() for msg in request.messages],
                        stream=True
                    )
                    
                    for chunk in stream:
                        content = chunk['message']['content']
                        yield f"data: {json.dumps({'content': content})}\n\n"
                        
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # 非流式响应
            response = ollama.chat(
                model=request.model,
                messages=[msg.dict() for msg in request.messages],
                stream=False
            )
            return ChatResponse(response=response['message']['content'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@app.get("/models")
async def list_models():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama服务错误: {str(e)}")

@app.post("/models/download/{model_name}")
async def start_download(model_name: str, background_tasks: BackgroundTasks):
    if model_name in download_status and download_status[model_name]["status"] == "downloading":
        return {"status": "already_downloading"}
    background_tasks.add_task(download_model, model_name)
    return {"status": "started"}

@app.get("/models/download/{model_name}/status")
async def get_download_status(model_name: str):
    if model_name not in download_status:
        raise HTTPException(status_code=404, detail="下载任务不存在")
    return download_status[model_name]


@app.post("/search")
async def search(request: SearchRequest):
    try:
        results = WebSearch.search_duckduckgo(
            request.query, request.num_results)
        return {"results": [{"title": r.title, "snippet": r.snippet, "link": r.link} for r in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")
