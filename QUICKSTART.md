# 快速开始指南

本指南帮助你在5分钟内快速启动 Telegram 商户管理机器人。

## 前置条件

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Telegram Bot Token

## 方式一：Docker 部署（推荐）

### 1. 准备 Bot Token

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建机器人
3. 保存获得的 Token

### 2. 配置环境变量

创建 `.env` 文件（Windows用户可以直接复制.env.example并重命名）：

```bash
# Linux/Mac
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

编辑 `.env` 文件，至少修改以下配置：

```env
TELEGRAM_BOT_TOKEN=你的Bot Token
ADMIN_USER_IDS=你的Telegram用户ID
SECRET_KEY=随机生成的密钥
JWT_SECRET_KEY=随机生成的密钥
ENCRYPTION_KEY=32位随机字符串
```

> 💡 获取你的 Telegram ID: 在 Telegram 中找到 [@userinfobot](https://t.me/userinfobot)，发送任意消息即可获取。

### 3. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f bot

# 查看运行状态
docker-compose ps
```

### 4. 测试 Bot

在 Telegram 中搜索你的机器人并发送 `/start`

### 5. 停止服务

```bash
docker-compose down
```

## 方式二：本地开发

### 1. 克隆项目

```bash
git clone <repository-url>
cd bot
```

### 2. 安装依赖

**Linux/Mac:**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**Windows:**
```powershell
# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库

**PostgreSQL:**
```sql
-- 创建数据库
CREATE DATABASE merchant_bot_db;
CREATE USER merchant_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE merchant_bot_db TO merchant_user;
```

**启动 Redis:**
```bash
# Linux/Mac
redis-server

# Windows: 从官网下载并启动
# https://github.com/microsoftarchive/redis/releases
```

### 4. 配置环境变量

复制并编辑 `.env` 文件：

```bash
# Linux/Mac
cp .env.example .env

# Windows
copy .env.example .env
```

修改数据库连接：
```env
DATABASE_URL=postgresql+asyncpg://merchant_user:your_password@localhost:5432/merchant_bot_db
REDIS_URL=redis://localhost:6379/0
```

### 5. 初始化数据库

```bash
# 创建迁移（首次运行）
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 6. 启动服务

**终端1 - 启动Bot:**
```bash
python app/main.py
```

**终端2 - 启动Celery Worker（可选）:**
```bash
celery -A app.tasks.celery_tasks worker --loglevel=info
```

**终端3 - 启动Celery Beat（定时任务，可选）:**
```bash
celery -A app.tasks.celery_tasks beat --loglevel=info
```

### 7. 测试

在 Telegram 中搜索你的机器人并发送 `/start`

## 常用命令

### Bot 命令

- `/start` - 开始使用
- `/help` - 获取帮助
- `/balance` - 查询余额
- `/orders` - 查看订单
- `/history` - 交易历史
- `/upload` - 上传图片识别

### 管理员命令

- `/broadcast` - 发送广播
- `/stats` - 数据统计
- `/merchants` - 商户管理

## 功能测试

### 1. 测试商户注册

1. 发送 `/start`
2. 输入验证码（测试环境可使用任意6位数字）
3. 查看注册成功消息

### 2. 测试余额查询

1. 发送 `/balance`
2. 查看余额信息

### 3. 测试图片识别

1. 发送 `/upload`
2. 上传包含订单号的图片
3. 等待识别结果

### 4. 测试广播（管理员）

1. 发送 `/broadcast`
2. 选择广播类型
3. 输入消息内容
4. 确认发送

## 配置说明

### 必填配置

```env
# Telegram Bot配置
TELEGRAM_BOT_TOKEN=必填，从BotFather获取

# 管理员配置
ADMIN_USER_IDS=必填，你的Telegram用户ID

# 安全配置
SECRET_KEY=必填，随机字符串
JWT_SECRET_KEY=必填，随机字符串
ENCRYPTION_KEY=必填，32位随机字符串
```

### 数据库配置

```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Redis
REDIS_URL=redis://host:port/db
```

### OCR配置

```env
# 使用PaddleOCR（默认，免费）
OCR_ENGINE=paddleocr

# 或使用云服务（需要配置API密钥）
OCR_ENGINE=aliyun
ALIYUN_OCR_ACCESS_KEY_ID=你的AccessKeyId
ALIYUN_OCR_ACCESS_KEY_SECRET=你的AccessKeySecret
```

## 故障排查

### 1. Bot 无法启动

**错误: Invalid token**
- 检查 `TELEGRAM_BOT_TOKEN` 是否正确
- 确认 Token 没有多余的空格

**错误: Database connection failed**
- 检查 PostgreSQL 是否运行
- 验证数据库连接URL
- 确认数据库用户权限

### 2. Redis 连接失败

```bash
# 检查 Redis 是否运行
redis-cli ping

# 应该返回 PONG
```

### 3. OCR 识别失败

**首次运行慢：**
- PaddleOCR 首次运行会下载模型，需要等待

**识别不准确：**
- 确保图片清晰
- 订单号要完整可见
- 可以尝试使用云服务OCR

### 4. 查看日志

```bash
# Docker部署
docker-compose logs -f bot

# 本地部署
tail -f logs/app.log
```

## 生产环境检查清单

- [ ] 修改所有默认密码和密钥
- [ ] 配置正确的数据库连接
- [ ] 设置管理员ID
- [ ] 配置备份策略
- [ ] 启用HTTPS（webhook模式）
- [ ] 配置监控和告警
- [ ] 设置日志轮转
- [ ] 测试所有功能
- [ ] 准备回滚方案

## 下一步

- 📖 阅读 [完整文档](README.md)
- 🏗️ 了解 [系统架构](ARCHITECTURE.md)
- 🚀 查看 [部署指南](DEPLOYMENT.md)
- 🔧 自定义配置和功能

## 获取帮助

如遇问题：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索 [Issues](https://github.com/your-repo/issues)
3. 提交新的 Issue
4. 联系技术支持

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

