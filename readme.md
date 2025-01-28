# LLM Chat Interface

一个基于Ollama的本地LLM聊天界面，支持多种模型和实时下载功能。

## 环境要求

- Python 3.11+
- [Ollama](https://ollama.com/)
- Docker (可选，用于容器化部署)

## 本地运行

### 1. 安装依赖

#### Python环境

确保您的系统已安装Python 3.11或更高版本：

- **Windows**：从[Python官网](https://www.python.org/downloads/)下载并安装
- **macOS**：使用Homebrew安装：`brew install python@3.11`
- **Linux**：使用包管理器安装：
  ```bash
  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3.11
  
  # CentOS/RHEL
  sudo dnf install python3.11
  ```

#### 安装Ollama

- **Windows**：
  1. 从[Ollama官网](https://ollama.com/download)下载Windows安装包
  2. 运行安装程序并按照提示完成安装

- **macOS**：
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- **Linux**：
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
  注意：Linux系统需要先安装依赖：
  ```bash
  # Ubuntu/Debian
  sudo apt update && sudo apt install -y ca-certificates curl

  # CentOS/RHEL
  sudo dnf install -y curl
  ```

#### 安装项目依赖

克隆项目后，在项目根目录执行：

```bash
pip install -r requirements.txt
```

### 2. 启动服务

#### 方式一：直接运行

```bash
# 给启动脚本添加执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh
```

#### 方式二：使用Docker

```bash
# 构建并启动容器
docker-compose up --build
```

### 3. 访问服务

服务启动后，可以通过以下地址访问：

- Web界面：http://localhost:8501
- API接口：http://localhost:8000
- Ollama服务：http://localhost:11434

## 功能特点

- 支持多种LLM模型
- 实时模型下载功能
- 可调节的模型参数（温度等）
- 支持系统提示词
- 美观的Web界面
- RESTful API支持

## 目录结构

```
.
├── api.py          # FastAPI后端服务
├── webui.py        # Streamlit前端界面
├── start.sh        # 启动脚本
├── requirements.txt # Python依赖
├── Dockerfile      # Docker构建文件
└── docker-compose.yml # Docker编排文件
```

## API文档

启动服务后，可以通过访问 http://localhost:8000/docs 查看完整的API文档。

## 注意事项

1. 首次运行时会自动下载默认模型（deepseek-r1:7b），这可能需要一些时间
2. 确保系统中已正确安装并配置Python和Ollama
3. 使用Docker方式运行时，确保Docker服务已启动