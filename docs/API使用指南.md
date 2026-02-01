# Telegram Bot HTTP API 使用指南

## 概述

本系统提供HTTP API接口，允许外部系统通过HTTP请求向指定的Telegram群组发送广播消息。

## 快速开始

### 1. 配置API密钥

在 `.env` 文件中设置API密钥：

```bash
API_SECRET_KEY=your-strong-secret-key-here
```

### 2. 启动API服务器

```bash
python run_api.py
```

服务器默认运行在 `http://0.0.0.0:8000`

### 3. 访问API文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 1. 健康检查

**端点**: `GET /api/v1/health`

**说明**: 检查API服务是否正常运行（无需认证）

**请求示例**:
```bash
curl http://localhost:8000/api/v1/health
```

**响应示例**:
```json
{
  "status": "ok",
  "service": "telegram-bot-api",
  "version": "1.0.0"
}
```

---

### 2. 获取群组列表

**端点**: `GET /api/v1/groups`

**说明**: 获取所有已绑定的Telegram群组列表

**请求头**:
- `X-API-Key`: API密钥（必填）

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/groups" \
  -H "X-API-Key: your-api-secret-key"
```

**响应示例**:
```json
[
  {
    "group_id": -1001234567890,
    "group_name": "商户A群组",
    "merchant_code": "M001",
    "is_active": true
  },
  {
    "group_id": -1009876543210,
    "group_name": "商户B群组",
    "merchant_code": "M002",
    "is_active": true
  }
]
```

---

### 3. 定向群组广播

**端点**: `POST /api/v1/broadcast/groups`

**说明**: 向指定的群组发送广播消息

**请求头**:
- `X-API-Key`: API密钥（必填）
- `Content-Type`: application/json

**请求体参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| group_ids | array[int] | 是 | 目标群组ID列表 |
| message | string | 否* | 文本消息内容 |
| photo_url | string | 否* | 图片URL |
| caption | string | 否 | 图片说明文字 |

*注意: `message` 和 `photo_url` 至少提供一个

#### 示例1: 发送纯文本消息

```bash
curl -X POST "http://localhost:8000/api/v1/broadcast/groups" \
  -H "X-API-Key: your-api-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "group_ids": [-1001234567890, -1009876543210],
    "message": "📢 系统通知：今晚22:00进行系统维护，预计持续1小时。"
  }'
```

#### 示例1.1: 发送多行文本消息（支持换行）

```bash
curl -X POST "http://localhost:8000/api/v1/broadcast/groups" \
  -H "X-API-Key: your-api-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "group_ids": [-1001234567890],
    "message": "📢 系统通知\n\n维护时间：今晚22:00-23:00\n维护内容：系统升级\n\n期间服务将暂停，请提前做好准备。\n\n感谢您的理解与支持！"
  }'
```

**Python示例（更清晰）:**
```python
import requests

message = """📢 系统通知

维护时间：今晚22:00-23:00
维护内容：系统升级

期间服务将暂停，请提前做好准备。

感谢您的理解与支持！"""

data = {
    "group_ids": [-1001234567890],
    "message": message
}

response = requests.post(
    "http://localhost:8000/api/v1/broadcast/groups",
    headers={"X-API-Key": "your-api-key", "Content-Type": "application/json"},
    json=data
)
```

#### 示例2: 发送图片消息

```bash
curl -X POST "http://localhost:8000/api/v1/broadcast/groups" \
  -H "X-API-Key: your-api-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "group_ids": [-1001234567890],
    "photo_url": "https://example.com/images/notice.jpg",
    "caption": "新功能上线通知"
  }'
```

#### 示例3: 发送图片+多行说明文字

```bash
curl -X POST "http://localhost:8000/api/v1/broadcast/groups" \
  -H "X-API-Key: your-api-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "group_ids": [-1001234567890],
    "photo_url": "https://example.com/images/promotion.jpg",
    "caption": "🎉 限时优惠活动\n\n活动时间：2月1日-2月7日\n优惠力度：全场8折\n\n详情请查看图片"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "广播完成: 成功 2/2 个群组",
  "total": 2,
  "success_count": 2,
  "failed_count": 0,
  "failed_groups": []
}
```

**失败响应示例**:
```json
{
  "success": true,
  "message": "广播完成: 成功 1/2 个群组",
  "total": 2,
  "success_count": 1,
  "failed_count": 1,
  "failed_groups": [
    {
      "group_id": -1009876543210,
      "error": "Forbidden: bot was kicked from the supergroup chat"
    }
  ]
}
```

## Python 调用示例

```python
import requests

API_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-secret-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 1. 获取群组列表
response = requests.get(f"{API_URL}/groups", headers=headers)
groups = response.json()
print(f"共有 {len(groups)} 个群组")

# 2. 发送简单广播
broadcast_data = {
    "group_ids": [g["group_id"] for g in groups],
    "message": "📢 这是一条测试广播消息"
}

response = requests.post(
    f"{API_URL}/broadcast/groups",
    headers=headers,
    json=broadcast_data
)

result = response.json()
print(f"广播结果: {result['message']}")
print(f"成功: {result['success_count']}, 失败: {result['failed_count']}")

# 3. 发送多行文本广播（支持换行）
multiline_message = """📢 重要通知

尊敬的用户：

系统将于今晚22:00进行维护升级，具体安排如下：

⏰ 维护时间：22:00 - 23:00
🔧 维护内容：系统功能升级
⚠️ 影响范围：所有服务暂停

请您提前做好准备，给您带来的不便敬请谅解。

感谢您的支持！"""

broadcast_data = {
    "group_ids": [groups[0]["group_id"]],  # 发送到第一个群组
    "message": multiline_message
}

response = requests.post(
    f"{API_URL}/broadcast/groups",
    headers=headers,
    json=broadcast_data
)

# 4. 发送图片+多行说明
image_broadcast = {
    "group_ids": [g["group_id"] for g in groups],
    "photo_url": "https://example.com/promotion.jpg",
    "caption": """🎉 新春特惠活动

活动时间：2月1日-2月7日
优惠内容：全场商品8折
参与方式：直接下单即可

详情请查看海报 👆"""
}

response = requests.post(
    f"{API_URL}/broadcast/groups",
    headers=headers,
    json=image_broadcast
)
```

## JavaScript/Node.js 调用示例

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000/api/v1';
const API_KEY = 'your-api-secret-key';

const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
};

// 1. 获取群组列表
async function getGroups() {
  const response = await axios.get(`${API_URL}/groups`, { headers });
  return response.data;
}

// 2. 发送广播
async function sendBroadcast(groupIds, message) {
  const response = await axios.post(
    `${API_URL}/broadcast/groups`,
    {
      group_ids: groupIds,
      message: message
    },
    { headers }
  );
  return response.data;
}

// 使用示例
(async () => {
  try {
    const groups = await getGroups();
    console.log(`共有 ${groups.length} 个群组`);
    
    const groupIds = groups.map(g => g.group_id);
    const result = await sendBroadcast(groupIds, '📢 测试广播消息');
    
    console.log(`广播结果: ${result.message}`);
    console.log(`成功: ${result.success_count}, 失败: ${result.failed_count}`);
  } catch (error) {
    console.error('错误:', error.response?.data || error.message);
  }
})();
```

## 错误码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | API密钥无效或未提供 |
| 404 | 资源不存在（如群组ID无效） |
| 500 | 服务器内部错误 |

## 安全建议

1. **保护API密钥**: 不要在代码中硬编码API密钥，使用环境变量
2. **使用HTTPS**: 生产环境务必使用HTTPS加密传输
3. **限制访问**: 在防火墙或反向代理中限制API访问来源
4. **定期更换密钥**: 定期更换API_SECRET_KEY
5. **监控日志**: 定期检查API访问日志，发现异常及时处理

## 部署建议

### 使用Nginx反向代理

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 使用systemd管理服务

创建 `/etc/systemd/system/telegram-bot-api.service`:

```ini
[Unit]
Description=Telegram Bot API Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python run_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-api
sudo systemctl start telegram-bot-api
```

## 常见问题

### Q1: 如何获取群组ID？

在群组中发送 `/get_chat_id` 命令，Bot会返回群组ID。

### Q2: 为什么发送失败？

可能原因：
- Bot未被添加到群组
- Bot在群组中没有发送消息权限
- 群组ID错误
- 图片URL无法访问

### Q3: 如何批量发送到所有群组？

先调用 `/api/v1/groups` 获取所有群组ID，然后在广播请求中使用这些ID。

### Q4: 发送频率有限制吗？

Telegram对Bot发送消息有频率限制（约30条/秒）。系统已内置延迟机制（BROADCAST_DELAY_MS配置），避免触发限流。

---

**最后更新**: 2025-02-01
