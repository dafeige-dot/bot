@echo off
REM 修复数据库并启动

echo ========================================
echo   修复数据库并启动 Bot
echo ========================================
echo.

REM 激活虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo 步骤 1: 重置数据库...
call reset_db.bat

echo.
echo 步骤 2: 检查配置...
python check_config.py

if %ERRORLEVEL% NEQ 0 (
    echo [错误] 配置检查失败
    pause
    exit /b 1
)

echo.
echo 步骤 3: 启动 Bot...
echo.
python app/main.py

