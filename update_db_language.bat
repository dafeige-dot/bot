@echo off
chcp 65001 >nul
echo ====================================
echo 数据库添加语言字段
echo ====================================
echo.

echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 正在执行数据库更新...
python update_db_language.py

echo.
echo ====================================
echo 完成！
echo ====================================
pause


