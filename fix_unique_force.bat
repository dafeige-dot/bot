@echo off
chcp 65001 >nul
echo ============================================================
echo 强制移除 merchant_code 唯一约束工具
echo ============================================================
echo.

echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 正在执行强制修复...
python fix_unique_constraint_force.py

echo.
echo ============================================================
echo 按任意键退出...
pause >nul

