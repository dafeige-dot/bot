#!/bin/bash

# Docker 环境升级脚本 - 添加 enable_ocr 字段
# 用途：升级数据库结构，添加会话级别的 OCR 开关功能

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  机器人 Docker 环境升级脚本"
echo "  功能：添加会话级别 OCR 开关"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 docker-compose 是否存在
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: docker-compose 未安装${NC}"
    exit 1
fi

# 检查容器是否运行
echo -e "${YELLOW}[1/6] 检查容器状态...${NC}"
if ! docker-compose ps | grep -q "merchant_bot_app"; then
    echo -e "${RED}错误: 容器未运行，请先启动服务${NC}"
    echo "运行: docker-compose up -d"
    exit 1
fi
echo -e "${GREEN}✓ 容器运行正常${NC}"
echo ""

# 备份数据库
echo -e "${YELLOW}[2/6] 备份数据库...${NC}"
BACKUP_DIR="./backups"
BACKUP_FILE="${BACKUP_DIR}/backup_before_ocr_upgrade_$(date +%Y%m%d_%H%M%S).sql"
mkdir -p ${BACKUP_DIR}

# 根据数据库类型选择备份方式
if grep -q "postgresql" .env 2>/dev/null || grep -q "DATABASE_URL.*postgres" .env 2>/dev/null; then
    echo "检测到 PostgreSQL 数据库，开始备份..."
    docker-compose exec -T postgres pg_dump -U merchant_user merchant_bot_db > ${BACKUP_FILE}
    echo -e "${GREEN}✓ PostgreSQL 数据库已备份到: ${BACKUP_FILE}${NC}"
elif grep -q "sqlite" .env 2>/dev/null || [ -f "merchant_bot.db" ]; then
    echo "检测到 SQLite 数据库，开始备份..."
    if [ -f "merchant_bot.db" ]; then
        cp merchant_bot.db ${BACKUP_FILE}.db
        echo -e "${GREEN}✓ SQLite 数据库已备份到: ${BACKUP_FILE}.db${NC}"
    else
        echo -e "${YELLOW}⚠ 未找到 SQLite 数据库文件${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 无法确定数据库类型，跳过备份${NC}"
fi
echo ""

# 拉取最新代码（如果需要）
echo -e "${YELLOW}[3/6] 更新代码...${NC}"
read -p "是否需要从 Git 拉取最新代码? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git pull
    echo -e "${GREEN}✓ 代码已更新${NC}"
else
    echo -e "${YELLOW}⚠ 跳过代码更新${NC}"
fi
echo ""

# 重新构建镜像
echo -e "${YELLOW}[4/6] 重新构建 Docker 镜像...${NC}"
docker-compose build --no-cache bot
echo -e "${GREEN}✓ 镜像构建完成${NC}"
echo ""

# 执行数据库迁移
echo -e "${YELLOW}[5/6] 执行数据库迁移...${NC}"
echo "正在添加 enable_ocr 字段到 merchants 表..."

# 方法1：使用 Alembic（推荐）
if docker-compose exec -T bot python -c "import alembic" 2>/dev/null; then
    echo "使用 Alembic 执行迁移..."
    docker-compose exec -T bot alembic upgrade head
    echo -e "${GREEN}✓ Alembic 迁移执行成功${NC}"
else
    # 方法2：直接执行 SQL
    echo "Alembic 不可用，使用 SQL 直接迁移..."
    
    if grep -q "postgresql" .env 2>/dev/null; then
        echo "执行 PostgreSQL 迁移..."
        docker-compose exec -T postgres psql -U merchant_user -d merchant_bot_db -c \
            "ALTER TABLE merchants ADD COLUMN IF NOT EXISTS enable_ocr BOOLEAN NOT NULL DEFAULT TRUE;"
        docker-compose exec -T postgres psql -U merchant_user -d merchant_bot_db -c \
            "COMMENT ON COLUMN merchants.enable_ocr IS '是否启用OCR图片识别';"
        echo -e "${GREEN}✓ PostgreSQL 迁移执行成功${NC}"
    elif grep -q "sqlite" .env 2>/dev/null; then
        echo "执行 SQLite 迁移..."
        docker-compose exec -T bot python -c "
from app.database.session import engine
import sqlalchemy as sa
with engine.begin() as conn:
    try:
        conn.execute(sa.text('ALTER TABLE merchants ADD COLUMN enable_ocr BOOLEAN NOT NULL DEFAULT 1'))
        print('✓ SQLite 迁移执行成功')
    except Exception as e:
        if 'duplicate column name' in str(e).lower():
            print('⚠ 字段已存在，跳过')
        else:
            raise
"
    else
        echo -e "${RED}错误: 无法确定数据库类型${NC}"
        exit 1
    fi
fi
echo ""

# 重启服务
echo -e "${YELLOW}[6/6] 重启服务...${NC}"
docker-compose restart bot
echo -e "${GREEN}✓ 服务已重启${NC}"
echo ""

# 验证升级
echo -e "${YELLOW}验证升级结果...${NC}"
sleep 3

# 检查容器状态
if docker-compose ps | grep -q "merchant_bot_app.*Up"; then
    echo -e "${GREEN}✓ 容器运行正常${NC}"
else
    echo -e "${RED}✗ 容器启动失败，请查看日志${NC}"
    docker-compose logs --tail=50 bot
    exit 1
fi

# 检查数据库字段
echo "检查数据库字段..."
if grep -q "postgresql" .env 2>/dev/null; then
    FIELD_EXISTS=$(docker-compose exec -T postgres psql -U merchant_user -d merchant_bot_db -t -c \
        "SELECT column_name FROM information_schema.columns WHERE table_name='merchants' AND column_name='enable_ocr';" | xargs)
    if [ "$FIELD_EXISTS" = "enable_ocr" ]; then
        echo -e "${GREEN}✓ enable_ocr 字段已成功添加${NC}"
    else
        echo -e "${RED}✗ enable_ocr 字段未找到${NC}"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  升级完成！${NC}"
echo "=========================================="
echo ""
echo "📝 升级内容："
echo "  • 添加了 enable_ocr 字段到 merchants 表"
echo "  • 支持会话级别的 OCR 开关控制"
echo "  • 默认所有会话开启 OCR"
echo ""
echo "🎮 使用方法："
echo "  在 Telegram 中执行："
echo "  /toggle_ocr       # 查看当前会话状态"
echo "  /toggle_ocr on    # 开启当前会话的OCR"
echo "  /toggle_ocr off   # 关闭当前会话的OCR"
echo ""
echo "📚 详细文档："
echo "  • README_OCR_TOGGLE.md - 快速参考"
echo "  • docs/OCR开关使用说明.md - 详细说明"
echo "  • docs/数据库迁移说明.md - 迁移指南"
echo ""
echo "📊 查看日志："
echo "  docker-compose logs -f bot"
echo ""
echo "🔄 如需回滚："
echo "  1. 停止服务: docker-compose stop bot"
echo "  2. 恢复备份: 参考 docs/数据库迁移说明.md"
echo "  3. 启动服务: docker-compose start bot"
echo ""
