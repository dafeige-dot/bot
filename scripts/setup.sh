#!/bin/bash

# 初始化项目脚本

echo "========================================="
echo "  Telegram 商户管理机器人 - 初始化"
echo "========================================="
echo ""

# 检查Python版本
echo "1. 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python版本: $python_version"

# 创建虚拟环境
echo ""
echo "2. 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✓ 虚拟环境创建成功"
else
    echo "   虚拟环境已存在"
fi

# 激活虚拟环境
echo ""
echo "3. 激活虚拟环境..."
source venv/bin/activate || . venv/Scripts/activate
echo "   ✓ 虚拟环境已激活"

# 安装依赖
echo ""
echo "4. 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✓ 依赖安装完成"

# 复制环境变量文件
echo ""
echo "5. 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✓ .env 文件已创建"
    echo "   ⚠️  请编辑 .env 文件并填入您的配置"
else
    echo "   .env 文件已存在"
fi

# 创建必要的目录
echo ""
echo "6. 创建目录结构..."
mkdir -p logs uploads temp backups migrations/versions
echo "   ✓ 目录创建完成"

# 初始化数据库迁移
echo ""
echo "7. 初始化数据库迁移..."
if [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions)" ]; then
    alembic revision --autogenerate -m "Initial migration"
    echo "   ✓ 数据库迁移文件创建完成"
else
    echo "   迁移文件已存在"
fi

echo ""
echo "========================================="
echo "  初始化完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，填入您的配置（特别是 TELEGRAM_BOT_TOKEN）"
echo "2. 启动数据库服务（如使用Docker: docker-compose up -d postgres redis）"
echo "3. 运行数据库迁移: alembic upgrade head"
echo "4. 启动Bot: python app/main.py"
echo ""
echo "或者使用 Docker Compose 一键启动："
echo "   docker-compose up -d"
echo ""

