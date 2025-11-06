# 系统架构文档

## 概述

本文档详细介绍 Telegram 商户管理机器人的系统架构设计。

## 技术栈

### 后端技术
- **Python 3.11+**: 主要开发语言
- **python-telegram-bot 20.x**: Telegram Bot框架
- **FastAPI**: 高性能Web框架（用于管理后台API）
- **SQLAlchemy 2.0**: ORM框架
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和消息队列
- **Celery**: 异步任务队列

### OCR识别
- **PaddleOCR**: 开源OCR引擎（默认）
- **阿里云OCR**: 商业OCR服务（可选）
- **腾讯云OCR**: 商业OCR服务（可选）
- **百度OCR**: 商业OCR服务（可选）

### 部署运维
- **Docker & Docker Compose**: 容器化部署
- **Alembic**: 数据库迁移工具
- **Loguru**: 日志管理
- **Prometheus**: 监控指标（可选）
- **Sentry**: 错误追踪（可选）

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        Telegram Cloud                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ (Polling / Webhook)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                         Bot Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Handlers   │  │   Commands   │  │  Callbacks   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                       Service Layer                          │
│  ┌───────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Merchant  │  │  Balance  │  │  Order   │  │   OCR    │ │
│  │  Service  │  │  Service  │  │ Service  │  │ Service  │ │
│  └───────────┘  └───────────┘  └──────────┘  └──────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              Broadcast Service                         │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼──────┐    ┌──────────▼─────────┐   ┌──────▼──────┐
│  PostgreSQL  │    │       Redis        │   │   Celery    │
│  (数据存储)   │    │  (缓存/消息队列)    │   │ (异步任务)   │
└──────────────┘    └────────────────────┘   └─────────────┘
```

### 分层架构

#### 1. 表示层 (Presentation Layer)

**Bot Layer - 机器人层**
- `handlers.py`: 处理各类消息（文本、图片等）
- `commands.py`: 处理命令（/start, /balance等）
- `callbacks.py`: 处理按钮回调
- `keyboards.py`: 键盘布局定义

#### 2. 业务逻辑层 (Business Logic Layer)

**Service Layer - 服务层**
- `MerchantService`: 商户管理服务
  - 商户注册、查询、更新
  - 商户状态管理
- `BalanceService`: 余额服务
  - 余额查询、充值、扣减
  - 冻结/解冻余额
  - 交易记录管理
- `OrderService`: 订单服务
  - 订单创建、查询、更新
  - 订单状态管理
  - 订单统计
- `OCRService`: OCR识别服务
  - 图片识别
  - 订单号提取
  - 多引擎支持
- `BroadcastService`: 广播服务
  - 全员广播
  - 分组广播
  - 发送状态跟踪

#### 3. 数据访问层 (Data Access Layer)

**Models - 数据模型**
- `Merchant`: 商户模型
- `Order`: 订单模型
- `Transaction`: 交易记录模型

**Database Session**
- 异步数据库连接池
- 会话管理
- 事务处理

#### 4. 基础设施层 (Infrastructure Layer)

- **数据库**: PostgreSQL持久化存储
- **缓存**: Redis缓存热点数据
- **消息队列**: Redis作为Celery的broker
- **任务队列**: Celery处理异步任务
- **日志系统**: Loguru统一日志管理

## 核心功能模块

### 1. 商户管理模块

**功能特性：**
- 商户注册与认证
- 商户信息管理
- 权限控制
- 活跃度追踪

**数据流程：**
```
用户 → /start命令 → 输入验证码 → 验证 → 创建商户 → 返回结果
```

**核心代码：**
- `app/models/merchant.py`: 商户数据模型
- `app/services/merchant.py`: 商户业务逻辑
- `app/bot/commands.py::start_command()`: 注册入口

### 2. 余额查询模块

**功能特性：**
- 实时余额查询
- 交易历史记录
- 余额变动通知
- 缓存优化

**数据流程：**
```
查询请求 → 检查缓存 → 查询数据库 → 计算余额 → 缓存结果 → 返回
```

**核心代码：**
- `app/models/transaction.py`: 交易记录模型
- `app/services/balance.py`: 余额服务
- `app/bot/commands.py::balance_command()`: 查询入口

### 3. 订单管理模块

**功能特性：**
- 订单列表查看
- 订单详情查询
- 订单搜索
- 订单状态跟踪

**数据流程：**
```
查询请求 → 解析参数 → 查询数据库 → 格式化数据 → 返回列表
```

**核心代码：**
- `app/models/order.py`: 订单数据模型
- `app/services/order.py`: 订单服务
- `app/bot/commands.py::orders_command()`: 查询入口

### 4. 图片识别模块

**功能特性：**
- 图片上传接收
- OCR文字识别
- 订单号提取
- 智能匹配查询

**技术实现：**
- 使用PaddleOCR进行文字识别
- 正则表达式提取订单号
- 支持多种订单号格式
- 异步处理提高性能

**数据流程：**
```
图片上传 → 下载保存 → OCR识别 → 提取订单号 → 查询订单 → 返回结果
```

**核心代码：**
- `app/services/ocr.py`: OCR识别服务
- `app/bot/handlers.py::photo_handler()`: 图片处理
- `app/tasks/celery_tasks.py::process_ocr_image()`: 异步任务

### 5. 广播推送模块

**功能特性：**
- 全员广播
- 分组广播
- 定时发送
- 发送状态追踪

**技术实现：**
- 使用Celery异步发送，避免阻塞
- 控制发送频率，防止触发限流
- 记录发送失败的用户
- 支持重试机制

**数据流程：**
```
管理员创建消息 → 选择目标 → 提交任务 → Celery处理 → 批量发送 → 统计结果
```

**核心代码：**
- `app/services/broadcast.py`: 广播服务
- `app/bot/commands.py::broadcast_command()`: 管理入口
- `app/tasks/celery_tasks.py::send_broadcast()`: 异步任务

## 数据库设计

### ER图

```
┌─────────────────┐
│    Merchants    │
├─────────────────┤
│ id (PK)         │
│ telegram_id     │
│ merchant_code   │
│ merchant_name   │
│ balance         │
│ frozen_balance  │
│ is_active       │
│ ...             │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐       ┌─────────────────┐
│     Orders      │       │  Transactions   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ merchant_id(FK) │◄─────►│ merchant_id(FK) │
│ order_no        │       │ transaction_no  │
│ amount          │       │ amount          │
│ order_status    │       │ balance_before  │
│ ...             │       │ balance_after   │
└─────────────────┘       │ ...             │
                          └─────────────────┘
```

### 表结构

#### merchants (商户表)
- 存储商户基本信息
- 余额数据
- 状态和权限

#### orders (订单表)
- 订单基本信息
- 支付状态
- 物流信息
- OCR识别结果

#### transactions (交易记录表)
- 交易流水
- 余额变动
- 关联订单

### 索引策略

- `merchants.telegram_id`: 唯一索引
- `merchants.merchant_code`: 唯一索引
- `orders.order_no`: 唯一索引
- `orders(merchant_id, created_at)`: 复合索引
- `transactions(merchant_id, created_at)`: 复合索引
- `transactions.transaction_no`: 唯一索引

## 性能优化

### 1. 缓存策略

**Redis缓存使用场景：**
- 余额查询结果（TTL: 60秒）
- 商户信息（TTL: 5分钟）
- 热点订单数据（TTL: 10分钟）

**缓存更新策略：**
- Write-Through: 写入时同时更新缓存
- Cache-Aside: 读取时检查缓存，miss时查询DB

### 2. 数据库优化

**连接池配置：**
```python
pool_size=20
max_overflow=10
pool_pre_ping=True
```

**查询优化：**
- 使用索引
- 避免N+1查询
- 分页查询
- 只查询需要的字段

### 3. 异步处理

**异步任务场景：**
- OCR图片识别
- 广播消息发送
- 数据统计计算
- 文件导出

**Celery配置：**
- Worker并发数: 4
- 任务超时: 30分钟
- 预取倍数: 4

### 4. 消息限流

**Telegram API限流：**
- 普通消息: 30条/秒
- 群组消息: 20条/分钟
- 全局限制: 避免触发限流

**实现方案：**
- 广播消息间隔100ms
- 使用队列控制发送速度
- 失败重试机制

## 安全设计

### 1. 数据安全

- 敏感信息加密存储
- 使用环境变量管理密钥
- 数据库连接加密
- 定期备份数据

### 2. 访问控制

- 基于Telegram ID的身份认证
- 角色权限管理（商户/管理员/超管）
- 操作日志记录
- API访问限流

### 3. 输入验证

- 参数类型检查
- 数据长度限制
- SQL注入防护
- XSS攻击防护

## 可扩展性设计

### 1. 水平扩展

**Bot实例：**
- 支持多实例部署
- 使用Webhook模式
- 负载均衡

**Celery Worker：**
- 增加Worker数量
- 任务优先级队列
- 分布式部署

**数据库：**
- 主从复制
- 读写分离
- 分库分表

### 2. 功能扩展

**插件化设计：**
- Service层独立
- 松耦合架构
- 易于添加新功能

**多租户支持：**
- 数据隔离
- 自定义配置
- 独立统计

## 监控和日志

### 1. 日志系统

**日志级别：**
- DEBUG: 调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

**日志输出：**
- 控制台输出（开发环境）
- 文件输出（生产环境）
- 错误日志单独记录

### 2. 监控指标

**系统指标：**
- CPU使用率
- 内存使用率
- 磁盘IO
- 网络流量

**业务指标：**
- 消息处理速度
- API响应时间
- 任务队列长度
- 数据库查询性能

**Prometheus指标：**
```python
# 消息处理计数
message_counter = Counter('bot_messages_total', 'Total messages')

# API响应时间
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

# 任务队列长度
task_queue_length = Gauge('celery_queue_length', 'Queue length')
```

## 部署架构

### 开发环境
```
单机部署
├── Bot进程
├── Celery Worker
├── PostgreSQL (本地)
└── Redis (本地)
```

### 生产环境（小规模）
```
Docker Compose
├── Bot容器 x 1
├── Celery Worker容器 x 2
├── PostgreSQL容器 x 1
├── Redis容器 x 1
└── Nginx容器 x 1 (可选)
```

### 生产环境（大规模）
```
Kubernetes集群
├── Bot Deployment (3 replicas)
├── Celery Deployment (5 replicas)
├── PostgreSQL StatefulSet (主从)
├── Redis StatefulSet (哨兵模式)
├── Ingress (负载均衡)
└── Monitoring (Prometheus + Grafana)
```

## 技术决策

### 为什么选择 Python？
- Telegram Bot SDK成熟
- OCR库支持完善
- 异步编程支持好
- 开发效率高

### 为什么选择 PostgreSQL？
- 功能强大
- 支持JSON类型
- 事务支持完善
- 生态系统成熟

### 为什么选择 Redis？
- 高性能缓存
- 支持多种数据结构
- 可作为消息队列
- 易于部署

### 为什么选择 Celery？
- 成熟的任务队列
- 支持定时任务
- 丰富的配置选项
- 监控工具完善

## 未来规划

### 短期计划
- [ ] 完善单元测试
- [ ] 添加API文档
- [ ] 实现数据导出功能
- [ ] 优化OCR识别准确率

### 中期计划
- [ ] 支持多语言
- [ ] 集成支付功能
- [ ] 移动端管理后台
- [ ] 智能客服机器人

### 长期计划
- [ ] AI智能推荐
- [ ] 大数据分析
- [ ] 微服务架构重构
- [ ] 全球化部署

## 参考资料

- [python-telegram-bot 文档](https://docs.python-telegram-bot.org/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Celery 文档](https://docs.celeryproject.org/)
- [PaddleOCR 文档](https://github.com/PaddlePaddle/PaddleOCR)

