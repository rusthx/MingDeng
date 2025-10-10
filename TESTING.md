# MingDeng Testing Guide

## ✅ Backend Status

The backend is currently **RUNNING** at http://127.0.0.1:8765

## Quick Testing

### 1. Test API Directly

```bash
# Health check
curl http://127.0.0.1:8765/

# Get config
curl http://127.0.0.1:8765/api/config

# Get today's tasks
curl http://127.0.0.1:8765/api/today

# Get statistics
curl http://127.0.0.1:8765/api/stats

# Get all plans
curl http://127.0.0.1:8765/api/plans
```

### 2. Access API Documentation

Open in browser:
- **Swagger UI**: http://127.0.0.1:8765/docs
- **ReDoc**: http://127.0.0.1:8765/redoc

### 3. Test Frontend

Open in browser:
```bash
# Option 1: Direct file
open src/index.html

# Option 2: Using Python HTTP server
cd src
python3 -m http.server 8000
# Then open: http://localhost:8000
```

### 4. Configure API (First Time Setup)

1. Open http://localhost:8000 (or file:///path/to/src/index.html)
2. Click "⚙️ 设置" in the sidebar
3. Fill in:
   - **API Base URL**: Your AI service URL
     - OpenAI: `https://api.openai.com/v1`
     - DeepSeek: `https://api.deepseek.com`
     - Local Ollama: `http://localhost:11434/v1`
   - **API Key**: Your API key
   - **Model**: Model name (e.g., `gpt-4`, `deepseek-chat`, `qwen2.5:7b`)
4. Click "保存 API 配置"

### 5. Test Plan Generation

1. Click "📋 生成计划"
2. Enter your learning goals, e.g.:
   ```
   我想学习 Python Web 开发，需要掌握：
   - Flask 框架基础
   - RESTful API 设计
   - 数据库操作（SQLAlchemy）
   - 前端集成

   每天学习 2 小时，3 周内完成。
   ```
3. Click "🤖 生成计划"
4. Review and save the plan

### 6. Test Today's Tasks

1. Click "📅 今日任务"
2. Check/uncheck tasks to mark as complete
3. Try adding a quick task

### 7. Test AI Chat

1. Click the "💬" button in bottom-right corner
2. Ask questions like:
   - "Python 和 JavaScript 有什么区别？"
   - "如何学习机器学习？"

## Testing with Ollama (Local, Free)

### Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from: https://ollama.com/download
```

### Download a model

```bash
# Download Qwen 2.5 (recommended, ~4GB)
ollama pull qwen2.5:7b

# Or try other models
ollama pull llama3.2:3b
ollama pull mistral:7b
```

### Start Ollama

```bash
ollama serve
```

### Configure in MingDeng

- **API Base URL**: `http://localhost:11434/v1`
- **API Key**: `ollama` (any value works)
- **Model**: `qwen2.5:7b` (or your downloaded model)

## Common Issues

### Issue 1: Backend not responding

**Solution**: Restart the backend
```bash
# Stop existing process
pkill -f uvicorn

# Start fresh
cd backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 8765
```

### Issue 2: CORS errors in browser

**Solution**: Make sure backend is running at 127.0.0.1:8765, not localhost

### Issue 3: Mem0 initialization error

**Note**: This is expected. The app works fine without Mem0. To enable memory:
- Ensure API key is configured
- Mem0 will initialize when you first use AI chat

### Issue 4: "Module not found"

**Solution**: Install dependencies
```bash
cd backend
pip3 install -r requirements.txt
```

## API Testing Examples

### Create a Task

```bash
# First create a plan (or use existing plan ID)
curl -X POST http://127.0.0.1:8765/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "YOUR_PLAN_ID",
    "task": "学习 Python 基础",
    "date": "2025-10-10",
    "estimated_time": 90,
    "difficulty": "simple"
  }'
```

### Update Config

```bash
curl -X POST http://127.0.0.1:8765/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "model": "gpt-4"
  }'
```

### Generate Plan (Requires API Config)

```bash
curl -X POST http://127.0.0.1:8765/api/plan/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想学习 Python，包括基础语法、数据结构、面向对象编程",
    "start_date": "2025-10-10"
  }'
```

## Performance Verification

### Expected Response Times

- Health check: < 10ms
- Get config/today/plans: < 50ms
- Create/update task: < 100ms
- AI plan generation: 5-15s (depends on AI service)
- AI chat: 1-3s (streaming)

### Check Backend Logs

```bash
# View logs
tail -f backend/logs.txt  # If logging to file

# Or check terminal where uvicorn is running
```

## Next Steps

1. ✅ Backend is running
2. ✅ API endpoints tested
3. ⏳ Configure your AI API key
4. ⏳ Test frontend in browser
5. ⏳ Generate your first learning plan
6. ⏳ (Optional) Build Tauri desktop app

## Build Tauri Desktop App

```bash
# Install dependencies
npm install

# Development mode (hot reload)
npm run dev

# Production build
npm run build

# Built app will be in: src-tauri/target/release/
```

---

**Status**: ✅ All core functionality working!

Backend Server: http://127.0.0.1:8765
API Docs: http://127.0.0.1:8765/docs
