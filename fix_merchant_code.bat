@echo off
chcp 65001 >nul
echo ============================================================
echo 移除 merchant_code 唯一约束工具
echo ============================================================
echo.

echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 正在执行数据库修复...
python fix_merchant_code_unique.py

echo.
echo ============================================================
echo 按任意键退出...
pause >nul

