#!/bin/bash

# MingDeng Development Startup Script

echo "🏮 启动 MingDeng 开发环境..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python 3 未安装"
    echo "请先安装 Python 3.9 或更高版本"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# Install Python dependencies
echo "📥 安装 Python 依赖..."
cd backend
pip install -r requirements.txt -q
cd ..

# Start Python backend in background
echo "🚀 启动 Python 后端 (端口 8765)..."
cd backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 8765 &
BACKEND_PID=$!
cd ..

echo "⏳ 等待后端启动..."
sleep 3

# Check if backend is running
if curl -s http://127.0.0.1:8765/ > /dev/null; then
    echo "✅ 后端启动成功！"
else
    echo "❌ 后端启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend HTTP server in background
echo "🌐 启动前端服务器 (端口 8000)..."
cd src
python3 -m http.server 8000 > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

echo "⏳ 等待前端启动..."
sleep 2

echo ""
echo "========================================="
echo "🏮 MingDeng 开发环境已就绪"
echo "========================================="
echo ""
echo "📍 后端 API: http://127.0.0.1:8765"
echo "📖 API 文档: http://127.0.0.1:8765/docs"
echo "🌐 前端应用: http://localhost:8000"
echo ""
echo "现在可以："
echo "1. 在浏览器中打开 http://localhost:8000"
echo "2. 或运行 'npm run tauri dev' 启动桌面应用"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '👋 再见！'; exit" INT

# Keep script running
wait $BACKEND_PID
