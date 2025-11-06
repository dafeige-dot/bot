#!/bin/bash

# 启动脚本

echo "正在启动 Telegram 商户管理机器人..."

# 检查环境变量
if [ ! -f .env ]; then
    echo "错误: .env 文件不存在"
    echo "请复制 .env.example 到 .env 并配置相关参数"
    exit 1
fi

# 创建必要的目录
mkdir -p logs uploads temp backups

# 检查数据库连接
echo "检查数据库连接..."
python -c "
from app.database.session import engine
import asyncio
async def check_db():
    try:
        async with engine.connect() as conn:
            print('✓ 数据库连接正常')
            return True
    except Exception as e:
        print(f'✗ 数据库连接失败: {e}')
        return False
asyncio.run(check_db())
"

if [ $? -ne 0 ]; then
    echo "数据库连接失败，请检查配置"
    exit 1
fi

# 运行数据库迁移
echo "运行数据库迁移..."
alembic upgrade head

if [ $? -ne 0 ]; then
    echo "数据库迁移失败"
    exit 1
fi

# 启动应用
echo "启动 Bot..."
python app/main.py

