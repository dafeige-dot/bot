# Docker 环境升级指南

## 升级内容

为机器人添加**会话级别的 OCR 开关**功能，需要升级数据库结构。

## 快速升级

### Windows 用户

```bash
# 直接运行升级脚本
upgrade_docker.bat
```

### Linux/Mac 用户

```bash
# 添加执行权限
chmod +x upgrade_docker.sh

# 运行升级脚本
./upgrade_docker.sh
```

## 升级步骤详解

### 1. 备份数据

**自动备份**（推荐）
- 升级脚本会自动备份数据库到 `backups/` 目录

**手动备份**
```bash
# PostgreSQL
docker-compose exec postgres pg_dump -U merchant_user merchant_bot_db > backups/manual_backup.sql

# SQLite
cp merchant_bot.db backups/manual_backup.db
```

### 2. 停止服务（可选）

如果需要零停机升级，可以跳过此步骤。

```bash
docker-compose stop bot
```

### 3. 更新代码

```bash
# 从 Git 拉取最新代码
git pull

# 或者手动复制新文件
# - app/models/merchant.py
# - app/bot/commands.py
# - app/bot/handlers.py
# - migrations/versions/add_enable_ocr_to_merchant.py
```

### 4. 重新构建镜像

```bash
# 重新构建 bot 服务镜像
docker-compose build --no-cache bot
```

### 5. 执行数据库迁移

#### 方法A：使用 Alembic（推荐）

```bash
# 进入容器执行迁移
docker-compose exec bot alembic upgrade head
```

#### 方法B：手动执行 SQL

**PostgreSQL**
```bash
docker-compose exec postgres psql -U merchant_user -d merchant_bot_db -c \
  "ALTER TABLE merchants ADD COLUMN IF NOT EXISTS enable_ocr BOOLEAN NOT NULL DEFAULT TRUE;"
```

**SQLite**
```bash
docker-compose exec bot python -c "
from app.database.session import engine
import sqlalchemy as sa
with engine.begin() as conn:
    conn.execute(sa.text('ALTER TABLE merchants ADD COLUMN enable_ocr BOOLEAN NOT NULL DEFAULT 1'))
"
```

### 6. 重启服务

```bash
# 重启 bot 服务
docker-compose restart bot

# 或者重启所有服务
docker-compose restart
```

### 7. 验证升级

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f bot

# 在 Telegram 中测试
# /toggle_ocr
```

## 验证清单

✅ **容器状态**
```bash
docker-compose ps
# 应该显示 bot 服务为 Up 状态
```

✅ **数据库字段**
```bash
# PostgreSQL
docker-compose exec postgres psql -U merchant_user -d merchant_bot_db -c \
  "SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_name='merchants' AND column_name='enable_ocr';"

# 应该显示 enable_ocr 字段
```

✅ **功能测试**
在 Telegram 中执行：
```
/toggle_ocr          # 应该显示当前会话状态
/toggle_ocr off      # 应该关闭当前会话的OCR
/toggle_ocr on       # 应该开启当前会话的OCR
```

## 常见问题

### Q1: 容器启动失败

**检查日志**
```bash
docker-compose logs --tail=100 bot
```

**常见原因**
- 数据库连接失败：检查 `.env` 中的数据库配置
- 端口冲突：检查端口是否被占用
- 依赖缺失：重新构建镜像 `docker-compose build --no-cache bot`

### Q2: 数据库迁移失败

**检查数据库连接**
```bash
# PostgreSQL
docker-compose exec postgres psql -U merchant_user -d merchant_bot_db -c "SELECT 1;"

# 应该返回 1
```

**手动执行迁移**
参考上面的"方法B：手动执行 SQL"

### Q3: 字段已存在错误

如果看到 "column already exists" 错误，说明字段已经添加，可以忽略。

```bash
# 验证字段是否存在
docker-compose exec postgres psql -U merchant_user -d merchant_bot_db -c \
  "SELECT column_name FROM information_schema.columns WHERE table_name='merchants' AND column_name='enable_ocr';"
```

### Q4: 需要回滚

**停止服务**
```bash
docker-compose stop bot
```

**恢复数据库**
```bash
# PostgreSQL
docker-compose exec -T postgres psql -U merchant_user -d merchant_bot_db < backups/backup_file.sql

# SQLite
cp backups/backup_file.db merchant_bot.db
```

**删除字段（如果需要）**
```bash
# PostgreSQL
docker-compose exec postgres psql -U merchant_user -d merchant_bot_db -c \
  "ALTER TABLE merchants DROP COLUMN IF EXISTS enable_ocr;"
```

**启动服务**
```bash
docker-compose start bot
```

## 零停机升级

如果需要零停机升级（生产环境推荐）：

### 1. 使用蓝绿部署

```bash
# 1. 构建新镜像
docker-compose build bot

# 2. 执行数据库迁移（不影响运行中的服务）
docker-compose exec bot alembic upgrade head

# 3. 启动新容器（使用不同名称）
docker-compose up -d --no-deps --scale bot=2 bot

# 4. 等待新容器就绪
sleep 10

# 5. 停止旧容器
docker-compose scale bot=1
```

### 2. 使用滚动更新

```bash
# 1. 执行数据库迁移
docker-compose exec bot alembic upgrade head

# 2. 滚动重启
docker-compose up -d --no-deps --build bot
```

## 升级后配置

### 环境变量

确保 `.env` 文件中有以下配置：

```bash
# 全局 OCR 开关（建议保持开启）
ENABLE_OCR=true
```

### 默认设置

- 新绑定的会话：默认开启 OCR
- 已存在的会话：迁移后默认开启 OCR
- 可以通过 `/toggle_ocr` 命令单独控制每个会话

## 监控和日志

### 实时日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 只查看 bot 服务日志
docker-compose logs -f bot

# 查看最近 100 行日志
docker-compose logs --tail=100 bot
```

### 健康检查

```bash
# 检查所有服务状态
docker-compose ps

# 检查特定服务
docker-compose ps bot
```

### 资源使用

```bash
# 查看容器资源使用情况
docker stats merchant_bot_app
```

## 性能优化建议

### 1. 数据库优化

```sql
-- 为 enable_ocr 字段添加索引（可选）
CREATE INDEX idx_merchants_enable_ocr ON merchants(enable_ocr);
```

### 2. 容器资源限制

在 `docker-compose.yml` 中添加：

```yaml
services:
  bot:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

## 相关文档

- `README_OCR_TOGGLE.md` - 快速参考
- `docs/OCR开关使用说明.md` - 详细使用说明
- `docs/数据库迁移说明.md` - 数据库迁移详情
- `upgrade_docker.sh` - Linux/Mac 升级脚本
- `upgrade_docker.bat` - Windows 升级脚本

## 技术支持

如遇到问题，请提供以下信息：

1. 容器日志：`docker-compose logs --tail=200 bot`
2. 容器状态：`docker-compose ps`
3. 数据库类型和版本
4. 错误信息截图

## 升级检查清单

升级完成后，请确认以下项目：

- [ ] 数据库已备份
- [ ] 代码已更新
- [ ] 镜像已重新构建
- [ ] 数据库迁移已执行
- [ ] 服务已重启
- [ ] 容器运行正常
- [ ] 日志无错误
- [ ] `/toggle_ocr` 命令可用
- [ ] 功能测试通过
- [ ] 文档已阅读
