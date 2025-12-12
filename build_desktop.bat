@echo off
setlocal enabledelayedexpansion

REM Build MingDeng desktop app with bundled Python backend (Windows).

pushd %~dp0

REM Ensure virtualenv exists
if not exist "backend-venv" (
    python -m venv backend-venv
)

REM Pick pip inside venv
set PIP_BIN=backend-venv\Scripts\pip.exe

if not exist "%PIP_BIN%" (
    echo ❌ 无法找到 %PIP_BIN% ，请检查 Python 和 venv
    exit /b 1
)

echo 📥 安装后端依赖...
%PIP_BIN% install -r backend\requirements.txt
if errorlevel 1 (
    echo ❌ 安装后端依赖失败
    exit /b 1
)

echo 📥 安装前端依赖...
npm install
if errorlevel 1 (
    echo ❌ npm install 失败
    exit /b 1
)

echo 🏗️ 构建 Tauri 安装包...
npx tauri build
if errorlevel 1 (
    echo ❌ 构建失败
    exit /b 1
)

echo ✅ 构建完成，安装包位于 src-tauri\target\release\bundle\

popd
endlocal
