# 部署指南

本文档介绍如何部署 Telegram 商户管理机器人。

## 目录

- [准备工作](#准备工作)
- [部署方式](#部署方式)
  - [Docker 部署（推荐）](#docker-部署推荐)
  - [手动部署](#手动部署)
  - [云服务器部署](#云服务器部署)
- [配置说明](#配置说明)
- [运维管理](#运维管理)

## 准备工作

### 1. 创建 Telegram Bot

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 保存获得的 **Bot Token**

### 2. 获取管理员 Telegram ID

1. 在 Telegram 中找到 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息获取您的 Telegram ID
3. 记录此 ID，将用于配置管理员权限

### 3. 准备服务器

**最低配置要求：**
- CPU: 2核
- 内存: 4GB
- 硬盘: 20GB
- 操作系统: Ubuntu 20.04+ / CentOS 7+ / Debian 10+

**推荐配置：**
- CPU: 4核
- 内存: 8GB
- 硬盘: 50GB SSD

## 部署方式

### Docker 部署（推荐）

#### 1. 安装 Docker 和 Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | bash
sudo apt-get install docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

#### 2. 克隆项目

```bash
git clone <repository-url>
cd bot
```

#### 3. 配置环境变量

```bash
cp .env.example .env
nano .env  # 或使用其他编辑器
```

**必填配置项：**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id
SECRET_KEY=generate_random_string_here
JWT_SECRET_KEY=generate_random_string_here
ENCRYPTION_KEY=generate_32_char_string_here
```

#### 4. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f bot

# 查看服务状态
docker-compose ps
```

#### 5. 初始化数据库

```bash
# 进入容器
docker-compose exec bot bash

# 运行迁移
alembic upgrade head

# 退出容器
exit
```

#### 6. 访问服务

- Bot: 在 Telegram 中搜索您的机器人
- Flower (Celery监控): http://your-server:5555
- API (如启用): http://your-server:8000

### 手动部署

#### 1. 安装依赖

```bash
# 安装系统依赖 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip python3-venv \
    postgresql-14 redis-server \
    libpq-dev python3-dev gcc g++

# 安装系统依赖 (CentOS/RHEL)
sudo yum install -y python3.11 python3-pip \
    postgresql14-server redis \
    postgresql-devel python3-devel gcc gcc-c++
```

#### 2. 设置数据库

```bash
# PostgreSQL
sudo -u postgres psql
CREATE DATABASE merchant_bot_db;
CREATE USER merchant_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE merchant_bot_db TO merchant_user;
\q

# 启动 Redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### 3. 配置项目

```bash
# 克隆项目
git clone <repository-url>
cd bot

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置
```

#### 4. 初始化数据库

```bash
# 运行迁移
alembic upgrade head
```

#### 5. 使用 systemd 管理服务

创建服务文件：

**Bot 服务：**
```bash
sudo nano /etc/systemd/system/merchant-bot.service
```

```ini
[Unit]
Description=Telegram Merchant Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
Environment="PATH=/path/to/bot/venv/bin"
ExecStart=/path/to/bot/venv/bin/python app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Celery Worker 服务：**
```bash
sudo nano /etc/systemd/system/merchant-bot-celery.service
```

```ini
[Unit]
Description=Merchant Bot Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
Environment="PATH=/path/to/bot/venv/bin"
ExecStart=/path/to/bot/venv/bin/celery -A app.tasks.celery_tasks worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start merchant-bot
sudo systemctl start merchant-bot-celery

# 开机自启
sudo systemctl enable merchant-bot
sudo systemctl enable merchant-bot-celery

# 查看状态
sudo systemctl status merchant-bot
sudo systemctl status merchant-bot-celery
```

### 云服务器部署

#### 阿里云 ECS / 腾讯云 CVM

1. 购买云服务器（推荐配置：2核4GB）
2. 安装 Docker 或按手动部署步骤操作
3. 配置安全组，开放必要端口（如需webhook模式需开放443）
4. 配置域名和SSL证书（webhook模式）

#### AWS / Azure / Google Cloud

类似流程，参考各平台文档。

#### Serverless 部署（高级）

可以使用 AWS Lambda / 阿里云函数计算 / 腾讯云 SCF：

1. 将代码打包
2. 配置触发器（Webhook模式）
3. 设置环境变量
4. 配置 API Gateway

> 注意：Serverless 部署需要修改部分代码以适配无状态环境。

## 配置说明

### 环境变量详解

详见 `.env.example` 文件中的注释。

### 使用 Webhook 模式

Webhook 模式更适合生产环境，需要：

1. 拥有域名和SSL证书
2. 配置 Nginx 反向代理
3. 修改 `.env`:

```env
BOT_MODE=webhook
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PORT=8443
```

**Nginx 配置示例：**

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /webhook {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 运维管理

### 日志查看

```bash
# Docker 部署
docker-compose logs -f bot
docker-compose logs -f celery_worker

# 手动部署
tail -f logs/app.log
tail -f logs/error.log
```

### 备份数据库

```bash
# 自动备份（已配置定时任务）
# 查看备份文件
ls -lh backups/

# 手动备份
docker-compose exec postgres pg_dump -U merchant_user merchant_bot_db > backup.sql
```

### 恢复数据库

```bash
docker-compose exec -T postgres psql -U merchant_user merchant_bot_db < backup.sql
```

### 更新部署

```bash
# Docker 部署
git pull
docker-compose build
docker-compose down
docker-compose up -d

# 手动部署
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart merchant-bot
sudo systemctl restart merchant-bot-celery
```

### 监控和告警

1. **Flower** (Celery监控): http://your-server:5555
2. **Prometheus + Grafana**: 配置 `PROMETHEUS_ENABLED=true`
3. **Sentry**: 配置 `SENTRY_DSN` 用于错误追踪

### 性能优化

1. **数据库优化**：
   - 添加索引
   - 定期清理旧数据
   - 使用连接池

2. **缓存优化**：
   - 合理使用 Redis 缓存
   - 设置适当的过期时间

3. **并发优化**：
   - 调整 Celery worker 数量
   - 使用消息队列处理高并发

## 安全建议

1. ✅ 使用强密码和密钥
2. ✅ 启用防火墙，只开放必要端口
3. ✅ 定期更新系统和依赖包
4. ✅ 配置 HTTPS（webhook模式）
5. ✅ 定期备份数据
6. ✅ 监控异常日志
7. ✅ 限制数据库访问权限
8. ✅ 使用环境变量存储敏感信息

## 故障排查

### Bot 无法启动

1. 检查 Token 是否正确
2. 检查数据库连接
3. 查看日志文件

### 数据库连接失败

1. 检查数据库服务是否运行
2. 验证数据库URL配置
3. 检查防火墙规则

### OCR 识别失败

1. 检查图片格式和大小
2. 查看 PaddleOCR 是否正确安装
3. 检查日志中的错误信息

## 技术支持

如遇问题，请：

1. 查看日志文件
2. 参考本文档
3. 提交 Issue
4. 联系技术支持

## 相关链接

- [README.md](README.md) - 项目介绍
- [开发文档](docs/) - 开发指南
- [API文档](docs/api.md) - API接口文档

