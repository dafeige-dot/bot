# Docker 部署指南

## 概述

本项目使用Docker Compose进行容器化部署，包含以下服务：

- **postgres** - PostgreSQL数据库
- **redis** - Redis缓存和消息队列
- **bot** - Telegram Bot主服务
- **api** - HTTP API服务（定向广播接口）

## 快速开始

### 1. 准备环境

确保已安装：
- Docker (>= 20.10)
- Docker Compose (>= 2.0)

### 2. 配置环境变量

复制并编辑 `.env` 文件：

```bash
cp env.template .env
nano .env
```

**必须配置的项：**

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token

# 管理员ID
ADMIN_USER_IDS=123456789,987654321

# 数据库（与docker-compose.yml保持一致）
DATABASE_URL=postgresql+asyncpg://merchant_user:merchant_password_2024@postgres:5432/merchant_bot_db

# Redis（与docker-compose.yml保持一致）
REDIS_URL=redis://:redis_password_2024@redis:6379/0

# API密钥（新增）
API_SECRET_KEY=your-strong-secret-key-here

# 安全密钥（运行 python generate_keys.py 生成）
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key-32-chars
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f bot
docker-compose logs -f api
```

### 4. 初始化数据库

```bash
# 进入bot容器
docker-compose exec bot bash

# 运行数据库迁移
alembic upgrade head

# 退出容器
exit
```

### 5. 验证部署

#### 检查服务状态

```bash
docker-compose ps
```

应该看到所有服务都是 `Up` 状态。

#### 检查Bot服务

在Telegram中向Bot发送 `/start`，应该收到欢迎消息。

#### 检查API服务

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 应该返回
# {"status":"ok","service":"telegram-bot-api","version":"1.0.0"}
```

或访问API文档：http://localhost:8000/docs

## 服务配置

### Bot服务

```yaml
bot:
  container_name: merchant_bot_app
  command: python run.py
  restart: unless-stopped
```

### API服务

```yaml
api:
  container_name: merchant_bot_api
  command: python run_api.py
  ports:
    - "${API_PORT:-8000}:8000"
  restart: unless-stopped
```

## 常用命令

### 启动和停止

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除数据卷（危险！会删除数据）
docker-compose down -v

# 重启特定服务
docker-compose restart bot
docker-compose restart api
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看Bot日志
docker-compose logs -f bot

# 查看API日志
docker-compose logs -f api

# 查看最近100行日志
docker-compose logs --tail=100 bot
```

### 进入容器

```bash
# 进入Bot容器
docker-compose exec bot bash

# 进入API容器
docker-compose exec api bash

# 进入数据库容器
docker-compose exec postgres psql -U merchant_user -d merchant_bot_db
```

### 更新代码

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 或者分步执行
docker-compose build
docker-compose up -d
```

### 备份和恢复

#### 备份数据库

```bash
# 创建备份
docker-compose exec postgres pg_dump -U merchant_user merchant_bot_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 或使用容器内的备份目录
docker-compose exec postgres pg_dump -U merchant_user merchant_bot_db > /backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 恢复数据库

```bash
# 从备份恢复
docker-compose exec -T postgres psql -U merchant_user merchant_bot_db < backup_20250201_120000.sql
```

## 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|---------|---------|------|
| postgres | 5432 | 5432 | PostgreSQL数据库 |
| redis | 6379 | 6379 | Redis缓存 |
| api | 8000 | 8000 | HTTP API服务 |

**注意**: Bot服务不需要暴露端口（使用Telegram长轮询）

## 环境变量

### 数据库连接

```bash
# Docker内部使用服务名
DATABASE_URL=postgresql+asyncpg://merchant_user:merchant_password_2024@postgres:5432/merchant_bot_db

# 外部访问使用localhost
DATABASE_URL=postgresql+asyncpg://merchant_user:merchant_password_2024@localhost:5432/merchant_bot_db
```

### Redis连接

```bash
# Docker内部
REDIS_URL=redis://:redis_password_2024@redis:6379/0

# 外部访问
REDIS_URL=redis://:redis_password_2024@localhost:6379/0
```

## 生产环境配置

### 1. 使用外部数据库

如果使用外部PostgreSQL：

```yaml
# docker-compose.yml
services:
  bot:
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@external-db:5432/dbname
```

### 2. 配置反向代理

使用Nginx作为反向代理：

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 限制资源使用

```yaml
services:
  bot:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 4. 配置日志轮转

```yaml
services:
  bot:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 监控和维护

### 健康检查

```bash
# 检查所有服务健康状态
docker-compose ps

# 检查API健康
curl http://localhost:8000/api/v1/health
```

### 查看资源使用

```bash
# 查看容器资源使用情况
docker stats

# 查看特定容器
docker stats merchant_bot_app merchant_bot_api
```

### 清理

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 清理所有未使用的资源
docker system prune -a
```

## 故障排查

### 问题1: 容器无法启动

```bash
# 查看详细日志
docker-compose logs bot

# 检查配置
docker-compose config

# 重新构建
docker-compose build --no-cache bot
```

### 问题2: 数据库连接失败

```bash
# 检查数据库是否就绪
docker-compose exec postgres pg_isready -U merchant_user

# 检查连接
docker-compose exec bot python -c "from app.database.session import engine; print('OK')"
```

### 问题3: API无法访问

```bash
# 检查端口是否被占用
netstat -tuln | grep 8000

# 检查容器端口映射
docker-compose port api 8000

# 检查防火墙
sudo ufw status
```

### 问题4: 权限问题

```bash
# 修复文件权限
sudo chown -R $USER:$USER logs uploads temp

# 或在容器内运行
docker-compose exec bot chown -R nobody:nogroup /app/logs
```

## 安全建议

1. **修改默认密码**: 更改 `docker-compose.yml` 中的数据库和Redis密码
2. **限制端口暴露**: 生产环境不要暴露数据库端口到公网
3. **使用secrets**: 敏感信息使用Docker secrets管理
4. **定期更新**: 定期更新基础镜像和依赖包
5. **备份数据**: 定期备份数据库和重要文件
6. **监控日志**: 配置日志收集和告警

## 升级指南

### 升级步骤

```bash
# 1. 备份数据
docker-compose exec postgres pg_dump -U merchant_user merchant_bot_db > backup_before_upgrade.sql

# 2. 拉取最新代码
git pull

# 3. 停止服务
docker-compose down

# 4. 重新构建
docker-compose build

# 5. 启动服务
docker-compose up -d

# 6. 运行数据库迁移（如果有）
docker-compose exec bot alembic upgrade head

# 7. 验证服务
docker-compose ps
curl http://localhost:8000/api/v1/health
```

## 附录

### docker-compose.yml 完整配置

参考项目根目录的 `docker-compose.yml` 文件。

### 环境变量清单

参考 `env.template` 文件。

---

**最后更新**: 2025-02-01
