@echo off
REM Windows 批处理脚本 - 设置 PostgreSQL 数据库

echo ========================================
echo   PostgreSQL 数据库初始化
echo ========================================
echo.

REM 设置 PostgreSQL 路径（根据你的安装路径调整）
set PGPATH="D:\soft\pgsql\bin"
set PGPASSWORD=Tczaflw@9527

echo 正在创建数据库和用户...
echo.

REM 使用 psql 执行 SQL
%PGPATH%\psql.exe -U postgres -h 127.0.0.1 -p 5432 -f setup_postgresql.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   数据库初始化成功！
    echo ========================================
    echo.
    echo 数据库信息：
    echo   数据库名: merchant_bot_db
    echo   用户名: merchant_user
    echo   密码: merchant_password_2024
    echo   主机: 127.0.0.1
    echo   端口: 5432
    echo.
    echo 请在 .env 文件中使用以下配置：
    echo DATABASE_URL=postgresql+asyncpg://merchant_user:merchant_password_2024@127.0.0.1:5432/merchant_bot_db
    echo.
) else (
    echo.
    echo [错误] 数据库初始化失败
    echo 请检查：
    echo 1. PostgreSQL 服务是否运行
    echo 2. postgres 用户密码是否正确
    echo 3. 端口 5432 是否可用
    echo.
)

pause

