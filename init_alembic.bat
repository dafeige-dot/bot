@echo off
REM 使用 Alembic 初始化数据库

echo ========================================
echo   使用 Alembic 初始化数据库
echo ========================================
echo.

REM 激活虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo 步骤 1: 创建迁移脚本...
alembic revision --autogenerate -m "Initial migration"

echo.
echo 步骤 2: 执行迁移...
alembic upgrade head

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   数据库迁移成功！
    echo ========================================
    echo.
) else (
    echo.
    echo [错误] 迁移失败
    echo.
)

pause

