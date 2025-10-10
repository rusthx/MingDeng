@echo off
REM MingDeng Development Startup Script for Windows

echo 🏮 启动 MingDeng 开发环境...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Python 未安装
    echo 请先安装 Python 3.9 或更高版本
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 创建 Python 虚拟环境...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 激活虚拟环境...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📥 安装 Python 依赖...
cd backend
pip install -r requirements.txt -q
cd ..

REM Start Python backend
echo 🚀 启动 Python 后端 (端口 8765)...
start "MingDeng Backend" cmd /k "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8765"

echo ⏳ 等待后端启动...
timeout /t 3 /nobreak >nul

REM Start frontend HTTP server
echo 🌐 启动前端服务器 (端口 8000)...
start "MingDeng Frontend" cmd /k "cd src && python -m http.server 8000"

echo ⏳ 等待前端启动...
timeout /t 2 /nobreak >nul

echo.
echo =========================================
echo 🏮 MingDeng 开发环境已就绪
echo =========================================
echo.
echo 📍 后端 API: http://127.0.0.1:8765
echo 📖 API 文档: http://127.0.0.1:8765/docs
echo 🌐 前端应用: http://localhost:8000
echo.
echo 现在可以：
echo 1. 在浏览器中打开 http://localhost:8000
echo 2. 或运行 'npm run tauri dev' 启动桌面应用
echo.
echo 关闭窗口可停止服务
echo.

pause
