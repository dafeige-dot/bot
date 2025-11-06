# 如何创建 .env 文件

## 快速开始

### 步骤 1: 复制模板文件

**Windows PowerShell:**
```powershell
Copy-Item env.template .env
```

**或者手动操作：**
1. 复制 `env.template` 文件
2. 重命名为 `.env`

### 步骤 2: 获取 Bot Token

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建机器人
3. 按提示设置名称和用户名
4. 复制获得的 Token

### 步骤 3: 获取你的 Telegram ID

1. 在 Telegram 中找到 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 复制返回的 ID

### 步骤 4: 生成安全密钥

运行密钥生成工具：
```bash
python generate_keys.py
```

复制输出的三个密钥。

### 步骤 5: 编辑 .env 文件

用记事本或其他编辑器打开 `.env` 文件，修改以下内容：

```env
# ===== 必填项 =====

# 1. 填入你的 Bot Token
TELEGRAM_BOT_TOKEN=你从BotFather获得的Token

# 2. 填入你的 Telegram ID
ADMIN_USER_IDS=你的Telegram用户ID
SUPER_ADMIN_ID=你的Telegram用户ID

# 3. 填入生成的密钥
SECRET_KEY=运行generate_keys.py得到的密钥1
JWT_SECRET_KEY=运行generate_keys.py得到的密钥2
ENCRYPTION_KEY=运行generate_keys.py得到的密钥3

# 4. 如果暂时不用OCR，设置为 false
ENABLE_OCR=false
```

### 步骤 6: 数据库配置（本地测试可暂时跳过）

如果使用 Docker：
```env
DATABASE_URL=postgresql+asyncpg://merchant_user:merchant_password_2024@postgres:5432/merchant_bot_db
REDIS_URL=redis://redis:6379/0
```

如果本地安装：
```env
DATABASE_URL=postgresql+asyncpg://merchant_user:your_password@localhost:5432/merchant_bot_db
REDIS_URL=redis://localhost:6379/0
```

## 完整的 .env 配置示例

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789
TELEGRAM_BOT_USERNAME=MyMerchantBot
BOT_MODE=polling

# 数据库
DATABASE_URL=postgresql+asyncpg://merchant_user:password123@localhost:5432/merchant_bot_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# OCR配置
OCR_ENGINE=paddleocr
ENABLE_OCR=false

# 管理员
ADMIN_USER_IDS=123456789
SUPER_ADMIN_ID=123456789

# 应用
APP_NAME=商户管理机器人
APP_ENV=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# 安全（请运行 python generate_keys.py 生成）
SECRET_KEY=H16d7oE8gvnP_4m0xs_zVc2SanSqQVZy6_od6P0XCkE
JWT_SECRET_KEY=eLAnOKQCr2rFAauYBRWN-sbgq06zrS4N66H9W6Cr2E4
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
ENCRYPTION_KEY=2n0KYX8xVQrtzfjUbY3yJ8jMpneY9GgI

# 日志
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=logs/app.log
LOG_ROTATION=100 MB
LOG_RETENTION=30 days

# 业务配置
MERCHANT_CODE_EXPIRE_MINUTES=30
BALANCE_CACHE_TTL=60
MAX_IMAGE_SIZE_MB=10
MAX_ORDER_RESULTS=10
BROADCAST_DELAY_MS=100

# 限流
RATE_LIMIT_PER_USER=20
OCR_RATE_LIMIT_PER_HOUR=50

# 第三方服务
SENTRY_DSN=
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=9090

# 文件存储
UPLOAD_DIR=uploads
TEMP_DIR=temp
STORAGE_TYPE=local

# 功能开关
ENABLE_OCR=false
ENABLE_BALANCE_QUERY=true
ENABLE_BROADCAST=true
REQUIRE_MERCHANT_AUTH=true

# 备份
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_PATH=backups/
```

## 验证配置

创建后验证配置是否正确：

```python
# 运行此命令检查配置
python -c "from app.config import settings; print('✅ 配置加载成功'); print(f'Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...')"
```

## 常见问题

### Q: .env 文件在哪里？
A: 在项目根目录（和 `README.md` 同级）

### Q: 为什么看不到 .env 文件？
A: Windows 默认隐藏以点开头的文件，在文件资源管理器中：
1. 点击"查看"
2. 勾选"隐藏的项目"

### Q: 必须填写所有配置吗？
A: 不是，只需要填写标记为"必填"的项目：
- `TELEGRAM_BOT_TOKEN`
- `ADMIN_USER_IDS`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `ENCRYPTION_KEY`

其他配置可以使用默认值。

## 下一步

创建好 `.env` 文件后：

```bash
# 1. 安装依赖
pip install -r requirements-no-ocr.txt

# 2. 启动 Bot
python app/main.py
```

