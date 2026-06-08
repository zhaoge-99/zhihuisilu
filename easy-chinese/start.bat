@echo off
chcp 65001 >nul
title Easy Chinese Server
echo.
echo ========================================
echo     Easy Chinese · 启动器
echo ========================================
echo.
echo 请在此输入你的 DeepSeek API Key:
set /p KEY="Key: "
if "%KEY%"=="" goto no_key

set DEEPSEEK_API_KEY=%KEY%
echo.
echo ✅ Key 已设置，正在启动服务器...
echo 启动后请打开 http://localhost:8000
echo 按 Ctrl+C 停止服务器
echo.
python "%~dp0server.py"
if %errorlevel% neq 0 python3 "%~dp0server.py"
pause
exit /b

:no_key
echo.
echo ⚠️ 必须输入 API Key 才能使用 AI 功能
echo 去 https://platform.deepseek.com/api_keys 获取
echo.
pause
