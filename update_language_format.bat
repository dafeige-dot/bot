@echo off
chcp 65001 >nul
echo ====================================
echo 更新数据库语言格式
echo Update Database Language Format
echo ====================================
echo.

echo 正在激活虚拟环境...
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 正在更新语言格式 (zh-CN -^> zh)...
echo Updating language format (zh-CN -^> zh)...
python update_language_format.py

echo.
echo ====================================
echo 完成！Complete!
echo ====================================
echo.
echo 现在可以启动Bot了
echo You can now start the bot
echo.
pause


