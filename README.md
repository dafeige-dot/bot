# Telegram 商户管理机器人

## 功能特性

- 📢 **广播推送**: 向所有商户或特定商户群组推送消息
- 💰 **余额查询**: 商户实时查询账户余额和交易记录
- 📸 **图片识别**: 上传订单截图，自动OCR识别并查找订单
- 🔐 **权限管理**: 商户认证和权限控制
- 📊 **数据统计**: 交易统计和数据分析

## 系统架构

```
┌─────────────────┐
│  Telegram Bot   │
│   (用户接口)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Bot Service    │
│  (业务逻辑层)    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│ 数据库│  │Redis │  │Celery│  │ OCR  │
│  层  │  │ 缓存 │  │ 队列 │  │ 服务 │
└──────┘  └──────┘  └──────┘  └──────┘
```

## 技术栈

- **开发语言**: Python 3.9+
- **Bot框架**: python-telegram-bot 20.x
- **Web框架**: FastAPI
- **数据库**: PostgreSQL
- **缓存**: Redis
- **OCR引擎**: PaddleOCR
- **任务队列**: Celery
- **ORM**: SQLAlchemy

## 项目结构

```
bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # 主入口
│   ├── config.py            # 配置文件
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers.py      # 消息处理器
│   │   ├── commands.py      # 命令处理
│   │   ├── callbacks.py     # 回调处理
│   │   └── keyboards.py     # 键盘布局
│   ├── services/
│   │   ├── __init__.py
│   │   ├── merchant.py      # 商户服务
│   │   ├── balance.py       # 余额服务
│   │   ├── order.py         # 订单服务
│   │   ├── broadcast.py     # 广播服务
│   │   └── ocr.py           # OCR识别服务
│   ├── models/
│   │   ├── __init__.py
│   │   ├── merchant.py      # 商户模型
│   │   ├── order.py         # 订单模型
│   │   └── transaction.py   # 交易模型
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py       # 数据库连接
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── celery_tasks.py  # 异步任务
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # 日志工具
│       └── helpers.py       # 辅助函数
├── migrations/              # 数据库迁移
├── tests/                   # 测试文件
├── docker-compose.yml       # Docker配置
├── Dockerfile
├── requirements.txt         # 依赖包
├── .env.example            # 环境变量模板
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd bot

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 3. 启动服务

```bash
# 启动数据库和Redis (使用Docker)
docker-compose up -d postgres redis

# 运行数据库迁移
alembic upgrade head

# 启动Celery Worker
celery -A app.tasks.celery_tasks worker --loglevel=info

# 启动Bot
python app/main.py
```

## 核心功能说明

### 1. 商户认证
- 商户首次使用需要通过验证码或邀请链接注册
- 绑定商户ID和Telegram账号

### 2. 余额查询
- 命令: `/balance` 或点击菜单按钮
- 显示当前余额、冻结金额、可用余额
- 支持查询交易历史

### 3. 广播消息
- 管理员专用功能
- 支持文字、图片、视频等多媒体消息
- 可选择全员广播或分组广播
- 支持定时发送

### 4. 图片识别订单
- 商户上传订单截图
- 自动OCR识别订单号
- 查询并返回订单详情
- 支持模糊匹配

## 环境变量说明

```env
# Telegram Bot配置
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/merchant_bot

# Redis配置
REDIS_URL=redis://localhost:6379/0

# OCR配置 (可选)
OCR_ENGINE=paddleocr  # 或 aliyun, tencentcloud
ALIYUN_OCR_ACCESS_KEY=
ALIYUN_OCR_SECRET_KEY=

# 管理员Telegram ID
ADMIN_USER_IDS=123456789,987654321

# 日志级别
LOG_LEVEL=INFO
```

## 部署方案

### 方案1: Docker部署 (推荐)
```bash
docker-compose up -d
```

### 方案2: 云服务器部署
- 使用systemd管理服务
- Nginx反向代理(如需webhook模式)
- 数据库使用云数据库服务

### 方案3: Serverless部署
- AWS Lambda / 阿里云函数计算
- 使用Webhook模式接收消息

## 安全建议

- ✅ 使用环境变量存储敏感信息
- ✅ 实现用户认证和授权
- ✅ 定期备份数据库
- ✅ 使用HTTPS和加密通信
- ✅ 限制API调用频率
- ✅ 记录操作日志

## 扩展功能

- [ ] 多语言支持
- [ ] 支付集成
- [ ] 数据导出功能
- [ ] 报表生成
- [ ] 智能客服对话

## 许可证

MIT License

