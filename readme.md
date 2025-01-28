# LLM Chat Interface

A local LLM chat interface based on Ollama, supporting multiple models and real-time model downloads.

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com/)
- Docker (optional, for containerized deployment)

## Local Setup

### 1. Install Dependencies

#### Python Environment

Ensure your system has Python 3.11 or higher installed:

- **Windows**: Download and install from [Python's official website](https://www.python.org/downloads/)
- **macOS**: Install using Homebrew: `brew install python@3.11`
- **Linux**: Install using package manager:
  ```bash
  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3.11
  
  # CentOS/RHEL
  sudo dnf install python3.11
  ```

#### Install Ollama

- **Windows**:
  1. Download Windows installer from [Ollama's website](https://ollama.com/download)
  2. Run the installer and follow the prompts

- **macOS**:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- **Linux**:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
  Note: Linux systems require installing dependencies first:
  ```bash
  # Ubuntu/Debian
  sudo apt update && sudo apt install -y ca-certificates curl

  # CentOS/RHEL
  sudo dnf install -y curl
  ```

#### Install Project Dependencies

After cloning the project, run in the project root directory:

```bash
pip install -r requirements.txt
```

### 2. Start Services

#### Option 1: Direct Run

```bash
# Add execute permission to start script
chmod +x start.sh

# Run start script
./start.sh
```

#### Option 2: Using Docker

```bash
# Build and start container
docker-compose up --build
```

### 3. Access Services

Once started, services are available at:

- Web Interface: http://localhost:8501
- API Endpoint: http://localhost:8000
- Ollama Service: http://localhost:11434

## Features

- Support for multiple LLM models
- Real-time model download capability
- Adjustable model parameters (temperature, etc.)
- System prompt support
- Beautiful web interface
- RESTful API support

## Project Structure

```
.
├── api.py          # FastAPI backend service
├── webui.py        # Streamlit frontend interface
├── start.sh        # Startup script
├── requirements.txt # Python dependencies
├── Dockerfile      # Docker build file
└── docker-compose.yml # Docker compose file
```

## API Documentation

After starting the service, view the complete API documentation at http://localhost:8000/docs.

## Notes

1. First run will automatically download the default model (deepseek-r1:7b), which may take some time
2. Ensure Python and Ollama are properly installed and configured on your system
3. When running with Docker, make sure the Docker service is started