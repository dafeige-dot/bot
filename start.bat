@echo off
REM Windows 启动脚本

echo ========================================
echo   Telegram 商户管理机器人
echo ========================================
echo.

REM 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo 正在激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 检查 .env 文件
if not exist ".env" (
    echo [错误] .env 文件不存在！
    echo 请先创建 .env 文件：
    echo   copy env.template .env
    echo 然后编辑配置。
    echo.
    pause
    exit /b 1
)

REM 设置 PYTHONPATH
set PYTHONPATH=%CD%

REM 启动 Bot
echo 正在启动 Bot...
echo.
python app/main.py

pause

