@echo off
REM 重置数据库脚本

echo ========================================
echo   重置 PostgreSQL 数据库
echo ========================================
echo.
echo 警告：此操作将删除所有数据！
echo.
pause

REM 设置 PostgreSQL 路径
set PGPATH="D:\soft\pgsql\bin"
set PGPASSWORD=Tczaflw@9527

echo 正在删除旧数据库...
%PGPATH%\psql.exe -U postgres -h 127.0.0.1 -p 5432 -c "DROP DATABASE IF EXISTS merchant_bot_db;"

echo 正在重新创建数据库...
%PGPATH%\psql.exe -U postgres -h 127.0.0.1 -p 5432 -f setup_postgresql.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   数据库重置成功！
    echo ========================================
    echo.
) else (
    echo.
    echo [错误] 数据库重置失败
    echo.
)

pause

