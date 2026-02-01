#!/bin/bash

# Docker Compose 快速启动脚本

set -e

echo "=========================================="
echo "  Telegram Bot Docker 部署脚本"
echo "=========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker未安装"
    echo "请先安装Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose未安装"
    echo "请先安装Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env文件不存在"
    echo "正在从env.template创建.env文件..."
    cp env.template .env
    echo "✅ .env文件已创建"
    echo ""
    echo "⚠️  请编辑.env文件，配置以下必填项："
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - ADMIN_USER_IDS"
    echo "  - API_SECRET_KEY"
    echo "  - SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY"
    echo ""
    read -p "是否现在编辑.env文件? (y/n): " edit_env
    if [ "$edit_env" = "y" ]; then
        ${EDITOR:-nano} .env
    else
        echo "请手动编辑.env文件后重新运行此脚本"
        exit 1
    fi
fi

echo "[1/5] 检查配置..."
# 检查必填配置
if ! grep -q "TELEGRAM_BOT_TOKEN=.*[^=]" .env; then
    echo "❌ 错误: TELEGRAM_BOT_TOKEN未配置"
    exit 1
fi

if ! grep -q "API_SECRET_KEY=.*[^=]" .env; then
    echo "⚠️  警告: API_SECRET_KEY未配置，API服务可能无法正常工作"
fi

echo "✅ 配置检查完成"
echo ""

echo "[2/5] 停止现有容器..."
docker-compose down
echo "✅ 现有容器已停止"
echo ""

echo "[3/5] 构建镜像..."
docker-compose build
echo "✅ 镜像构建完成"
echo ""

echo "[4/5] 启动服务..."
docker-compose up -d
echo "✅ 服务已启动"
echo ""

echo "[5/5] 等待服务就绪..."
sleep 5

# 检查服务状态
echo ""
echo "服务状态:"
docker-compose ps
echo ""

# 检查API健康
echo "检查API服务..."
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ API服务正常"
    echo "   访问API文档: http://localhost:8000/docs"
else
    echo "⚠️  API服务可能还在启动中，请稍后访问"
fi

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "📋 常用命令:"
echo "  查看日志:     docker-compose logs -f"
echo "  查看Bot日志:  docker-compose logs -f bot"
echo "  查看API日志:  docker-compose logs -f api"
echo "  停止服务:     docker-compose down"
echo "  重启服务:     docker-compose restart"
echo ""
echo "🌐 访问地址:"
echo "  API文档:      http://localhost:8000/docs"
echo "  健康检查:     http://localhost:8000/api/v1/health"
echo ""
echo "📚 更多信息请查看: docs/Docker部署指南.md"
echo ""
