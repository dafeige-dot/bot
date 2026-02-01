@echo off
chcp 65001 >nul
echo ========================================
echo Telegram Bot API 服务器启动脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境，请先运行 setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/2] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 启动API服务器
echo [2/2] 启动API服务器...
echo.
echo API文档地址: http://localhost:8000/docs
echo.
python run_api.py

pause
