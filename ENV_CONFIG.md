# 环境变量配置说明

## 快速配置

创建 `.env` 文件，复制以下内容并修改相应的值：

```env
# ===== Telegram Bot配置 =====
# 从 @BotFather 获取的 Bot Token（必填）
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Bot用户名（可选）
TELEGRAM_BOT_USERNAME=YourMerchantBot

# Bot运行模式: polling（轮询） 或 webhook（推荐生产环境使用）
BOT_MODE=polling

# ===== 数据库配置 =====
# PostgreSQL数据库连接URL（必填）
DATABASE_URL=postgresql+asyncpg://merchant_user:your_password@localhost:5432/merchant_bot_db

# 数据库连接池大小
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# ===== Redis配置 =====
# Redis连接URL（必填）
REDIS_URL=redis://localhost:6379/0

# ===== 管理员配置 =====
# 管理员的Telegram用户ID，多个用逗号分隔（必填）
# 获取方式：在Telegram中找 @userinfobot，发送任意消息获取ID
ADMIN_USER_IDS=123456789,987654321

# 超级管理员ID（拥有所有权限）
SUPER_ADMIN_ID=123456789

# ===== 安全配置 =====
# 应用密钥（必填，请修改为随机字符串）
SECRET_KEY=your-secret-key-change-this-in-production

# JWT密钥（必填，请修改为随机字符串）
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# 加密密钥（必填，32位字符串）
ENCRYPTION_KEY=your-encryption-key-32-characters

# ===== 日志配置 =====
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# ===== OCR配置 =====
# OCR引擎选择: paddleocr（免费）, aliyun, tencentcloud, baidu
OCR_ENGINE=paddleocr

# 是否启用OCR功能
ENABLE_OCR=true

# ===== 功能开关 =====
# 是否启用余额查询功能
ENABLE_BALANCE_QUERY=true

# 是否启用广播功能
ENABLE_BROADCAST=true

# 是否需要商户认证
REQUIRE_MERCHANT_AUTH=true
```

## 配置项详解

### 1. Telegram Bot配置

#### TELEGRAM_BOT_TOKEN（必填）
- **说明**: Telegram Bot的访问令牌
- **获取方式**: 
  1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
  2. 发送 `/newbot` 创建新机器人
  3. 按提示设置机器人名称和用户名
  4. 保存获得的Token
- **格式**: `数字:字母数字字符串`
- **示例**: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

#### BOT_MODE
- **说明**: Bot的运行模式
- **可选值**: 
  - `polling`: 轮询模式，适合开发和小规模部署
  - `webhook`: Webhook模式，适合生产环境
- **默认值**: `polling`

### 2. 数据库配置

#### DATABASE_URL（必填）
- **说明**: PostgreSQL数据库连接地址
- **格式**: `postgresql+asyncpg://用户名:密码@主机:端口/数据库名`
- **示例**: `postgresql+asyncpg://merchant_user:pass123@localhost:5432/merchant_bot_db`
- **注意**: 必须使用异步驱动 `asyncpg`

#### DATABASE_POOL_SIZE
- **说明**: 数据库连接池大小
- **默认值**: `20`
- **建议**: 根据并发量调整，小型应用10-20，中型应用20-50

### 3. Redis配置

#### REDIS_URL（必填）
- **说明**: Redis服务器连接地址
- **格式**: `redis://主机:端口/数据库编号`
- **示例**: `redis://localhost:6379/0`
- **带密码**: `redis://:密码@localhost:6379/0`

### 4. 管理员配置

#### ADMIN_USER_IDS（必填）
- **说明**: 管理员的Telegram用户ID列表
- **格式**: 多个ID用逗号分隔
- **示例**: `123456789,987654321,111222333`
- **获取方式**:
  1. 在Telegram中找到 [@userinfobot](https://t.me/userinfobot)
  2. 发送任意消息
  3. 复制返回的ID

#### SUPER_ADMIN_ID
- **说明**: 超级管理员ID，拥有最高权限
- **格式**: 单个Telegram用户ID
- **示例**: `123456789`

### 5. 安全配置

#### SECRET_KEY（必填）
- **说明**: 应用的主密钥，用于加密会话等
- **生成方式**:
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```
- **重要**: 生产环境务必修改，且不要泄露

#### JWT_SECRET_KEY（必填）
- **说明**: JWT令牌签名密钥
- **生成方式**: 同上
- **建议**: 使用不同于SECRET_KEY的值

#### ENCRYPTION_KEY（必填）
- **说明**: 数据加密密钥，必须是32位字符
- **生成方式**:
  ```python
  import secrets
  print(secrets.token_urlsafe(24))  # 会生成32个字符
  ```

### 6. OCR配置

#### OCR_ENGINE
- **说明**: OCR识别引擎选择
- **可选值**:
  - `paddleocr`: 免费开源OCR，无需API密钥
  - `aliyun`: 阿里云OCR，需配置AccessKey
  - `tencentcloud`: 腾讯云OCR，需配置SecretId/Key
  - `baidu`: 百度OCR，需配置AppId/ApiKey
- **默认值**: `paddleocr`
- **建议**: 开发测试用PaddleOCR，生产环境可考虑云服务

#### PaddleOCR配置
```env
PADDLEOCR_USE_GPU=false      # 是否使用GPU加速
PADDLEOCR_LANG=ch            # 语言：ch(中文), en(英文)
```

#### 阿里云OCR配置
```env
OCR_ENGINE=aliyun
ALIYUN_OCR_ACCESS_KEY_ID=你的AccessKeyId
ALIYUN_OCR_ACCESS_KEY_SECRET=你的AccessKeySecret
ALIYUN_OCR_REGION=cn-shanghai
```

#### 腾讯云OCR配置
```env
OCR_ENGINE=tencentcloud
TENCENT_SECRET_ID=你的SecretId
TENCENT_SECRET_KEY=你的SecretKey
TENCENT_OCR_REGION=ap-guangzhou
```

### 7. 功能开关

#### ENABLE_OCR
- **说明**: 是否启用图片识别功能
- **默认值**: `true`

#### ENABLE_BALANCE_QUERY
- **说明**: 是否启用余额查询功能
- **默认值**: `true`

#### ENABLE_BROADCAST
- **说明**: 是否启用广播功能
- **默认值**: `true`

#### REQUIRE_MERCHANT_AUTH
- **说明**: 是否需要商户认证才能使用
- **默认值**: `true`

### 8. 日志配置

#### LOG_LEVEL
- **说明**: 日志输出级别
- **可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **默认值**: `INFO`
- **建议**: 
  - 开发环境: `DEBUG`
  - 生产环境: `INFO` 或 `WARNING`

#### LOG_FILE_PATH
- **说明**: 日志文件路径
- **默认值**: `logs/app.log`

### 9. 业务配置

#### MERCHANT_CODE_EXPIRE_MINUTES
- **说明**: 商户验证码有效期（分钟）
- **默认值**: `30`

#### BALANCE_CACHE_TTL
- **说明**: 余额查询缓存时间（秒）
- **默认值**: `60`

#### MAX_IMAGE_SIZE_MB
- **说明**: 图片上传大小限制（MB）
- **默认值**: `10`

#### BROADCAST_DELAY_MS
- **说明**: 广播消息发送间隔（毫秒）
- **默认值**: `100`
- **建议**: 防止触发Telegram限流，不要设置太小

## 环境变量生成脚本

### 生成随机密钥

**Python脚本：**
```python
import secrets

print("=" * 50)
print("环境变量配置生成器")
print("=" * 50)
print()

print("SECRET_KEY:")
print(secrets.token_urlsafe(32))
print()

print("JWT_SECRET_KEY:")
print(secrets.token_urlsafe(32))
print()

print("ENCRYPTION_KEY (32字符):")
print(secrets.token_urlsafe(24))
print()

print("=" * 50)
print("请将以上密钥复制到 .env 文件中")
print("=" * 50)
```

保存为 `generate_keys.py` 并运行：
```bash
python generate_keys.py
```

## 不同环境的配置

### 开发环境

```env
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

DATABASE_URL=postgresql+asyncpg://localhost:5432/merchant_bot_dev
REDIS_URL=redis://localhost:6379/0

BOT_MODE=polling
```

### 测试环境

```env
APP_ENV=staging
DEBUG=false
LOG_LEVEL=INFO

DATABASE_URL=postgresql+asyncpg://test-db:5432/merchant_bot_staging
REDIS_URL=redis://test-redis:6379/0

BOT_MODE=polling
```

### 生产环境

```env
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING

DATABASE_URL=postgresql+asyncpg://prod-db:5432/merchant_bot_prod
REDIS_URL=redis://prod-redis:6379/0

BOT_MODE=webhook
WEBHOOK_URL=https://yourdomain.com/webhook

# 启用监控
PROMETHEUS_ENABLED=true
SENTRY_DSN=你的Sentry_DSN
```

## 配置验证

创建 `check_config.py` 脚本验证配置：

```python
from app.config import settings

print("配置检查")
print("=" * 50)

# 检查必填项
required_fields = [
    'TELEGRAM_BOT_TOKEN',
    'DATABASE_URL',
    'ADMIN_USER_IDS',
    'SECRET_KEY',
]

for field in required_fields:
    value = getattr(settings, field, None)
    status = "✓" if value else "✗"
    print(f"{status} {field}: {'已配置' if value else '未配置'}")

print("=" * 50)
```

## 常见问题

### Q: 如何获取Telegram Bot Token?
A: 在Telegram中找到 @BotFather，发送 `/newbot` 按提示创建。

### Q: 忘记了数据库密码怎么办？
A: 重新设置PostgreSQL用户密码，然后更新 `.env` 中的 `DATABASE_URL`。

### Q: 配置修改后需要重启吗？
A: 是的，环境变量只在程序启动时读取，修改后需要重启服务。

### Q: 可以在运行时修改配置吗？
A: 不建议。环境变量应该在部署时配置好，运行时不应修改。

### Q: 多个管理员如何配置？
A: 在 `ADMIN_USER_IDS` 中用逗号分隔多个ID，例如：`123,456,789`

## 安全建议

1. ✅ **永远不要**将 `.env` 文件提交到Git仓库
2. ✅ 生产环境使用强密码和随机密钥
3. ✅ 定期轮换密钥
4. ✅ 使用专用的数据库用户，限制权限
5. ✅ Redis设置访问密码
6. ✅ 使用环境变量管理服务（如AWS Secrets Manager）
7. ✅ 备份配置文件到安全位置

## 相关文档

- [快速开始](QUICKSTART.md)
- [部署指南](DEPLOYMENT.md)
- [系统架构](ARCHITECTURE.md)
- [README](README.md)

