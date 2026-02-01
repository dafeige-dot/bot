# 定向群组广播功能更新日志

## 版本: v1.1.0
## 日期: 2025-02-01

---

## 🎉 新增功能

### 1. Telegram Bot 定向群组广播命令

新增 `/dxgb` 命令，允许管理员通过可视化界面选择目标群组发送广播。

**功能特点:**
- ✅ 可视化群组选择（内联按钮）
- ✅ 支持多选和全选
- ✅ 实时显示选中状态
- ✅ 支持文字和图片消息
- ✅ 发送前预览确认
- ✅ 发送结果统计

**使用方法:**
```
/dxgb
```

### 2. HTTP API 接口

新增完整的HTTP API接口，支持外部系统调用。

**API端点:**
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/groups` - 获取群组列表
- `POST /api/v1/broadcast/groups` - 定向群组广播

**功能特点:**
- ✅ RESTful API设计
- ✅ API密钥认证
- ✅ 完整的API文档（Swagger UI）
- ✅ 支持文字和图片消息
- ✅ 批量发送支持
- ✅ 详细的错误信息

---

## 📁 新增文件

### Bot功能相关

| 文件 | 说明 |
|------|------|
| `app/bot/commands.py` | 新增 `dxgb_command` 函数 |
| `app/bot/callbacks.py` | 新增 `handle_dxgb_callback` 函数 |
| `app/bot/handlers.py` | 新增 `handle_dxgb_message` 和 `handle_dxgb_photo` 函数 |
| `app/main.py` | 注册 `/dxgb` 命令处理器 |

### API相关

| 文件 | 说明 |
|------|------|
| `app/api/__init__.py` | API模块初始化 |
| `app/api/app.py` | FastAPI应用配置 |
| `app/api/routes.py` | API路由定义 |
| `run_api.py` | API服务器启动脚本 |
| `start_api.bat` | Windows API启动脚本 |

### Docker部署相关

| 文件 | 说明 |
|------|------|
| `docker-compose.yml` | 更新API服务配置 |
| `Dockerfile` | 添加curl依赖，修复CMD命令 |
| `docker-start.sh` | Linux/Mac Docker启动脚本 |
| `docker-start.bat` | Windows Docker启动脚本 |
| `docs/Docker部署指南.md` | Docker部署完整文档 |

### 配置相关

| 文件 | 说明 |
|------|------|
| `app/config.py` | 新增 `API_SECRET_KEY` 配置项 |
| `env.template` | 新增API配置模板 |

### 文档相关

| 文件 | 说明 |
|------|------|
| `docs/API使用指南.md` | 详细的API使用文档 |
| `docs/定向广播功能说明.md` | 功能总体说明文档 |
| `README_API.md` | API快速开始指南 |
| `CHANGELOG_定向广播.md` | 本更新日志 |

### 测试和示例

| 文件 | 说明 |
|------|------|
| `test_api.py` | API自动化测试脚本 |
| `example_api_usage.py` | API交互式使用示例 |

---

## 🔧 修改的文件

### app/bot/commands.py
- ✅ 新增 `dxgb_command` 函数
- 实现群组列表展示和选择逻辑

### app/bot/callbacks.py
- ✅ 修改 `button_callback` 函数，添加dxgb回调处理
- ✅ 新增 `handle_dxgb_callback` 函数
- 实现群组选择、全选、确认等按钮逻辑

### app/bot/handlers.py
- ✅ 修改 `text_handler` 函数，添加dxgb消息处理
- ✅ 修改 `photo_handler` 函数，添加dxgb图片处理
- ✅ 新增 `handle_dxgb_message` 函数
- ✅ 新增 `handle_dxgb_photo` 函数

### app/main.py
- ✅ 注册 `/dxgb` 命令处理器

### app/config.py
- ✅ 新增 `API_SECRET_KEY` 配置项

### env.template
- ✅ 新增 `API_SECRET_KEY` 配置说明

---

## 📋 配置说明

### 环境变量

在 `.env` 文件中添加以下配置：

```bash
# API服务器配置
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-strong-secret-key-here
```

### 启动服务

**Bot服务（原有）:**
```bash
python run.py
```

**API服务（新增）:**
```bash
python run_api.py
# 或使用批处理文件
start_api.bat
```

---

## 🚀 使用示例

### 1. Bot命令方式

```
管理员: /dxgb
Bot: [显示群组选择界面]
管理员: [选择目标群组]
管理员: [点击确认发送]
管理员: 📢 系统通知内容
Bot: [显示预览]
管理员: 确认
Bot: ✅ 定向广播完成
```

### 2. HTTP API方式

```python
import requests

API_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-secret-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 获取群组列表
response = requests.get(f"{API_URL}/groups", headers=headers)
groups = response.json()

# 发送广播
data = {
    "group_ids": [g["group_id"] for g in groups],
    "message": "📢 系统通知"
}
response = requests.post(
    f"{API_URL}/broadcast/groups",
    headers=headers,
    json=data
)
print(response.json())
```

---

## 🧪 测试

### 运行API测试

```bash
python test_api.py
```

### 运行交互式示例

```bash
python example_api_usage.py
```

---

## 📚 文档

- **API文档**: http://localhost:8000/docs (启动API服务后访问)
- **详细指南**: [docs/API使用指南.md](docs/API使用指南.md)
- **功能说明**: [docs/定向广播功能说明.md](docs/定向广播功能说明.md)
- **快速开始**: [README_API.md](README_API.md)

---

## ⚠️ 注意事项

1. **API密钥安全**: 
   - 使用强密码
   - 不要在代码中硬编码
   - 定期更换密钥

2. **群组权限**:
   - Bot必须在目标群组中
   - Bot需要有发送消息权限
   - 群组必须已绑定商户

3. **发送限制**:
   - Telegram有频率限制
   - 系统已内置延迟机制
   - 建议分批发送大量消息

4. **生产环境**:
   - 使用HTTPS
   - 限制API访问来源
   - 配置防火墙规则
   - 监控日志文件

---

## 🐛 已知问题

无

---

## 🔮 未来计划

- [ ] 支持定时发送
- [ ] 支持消息模板
- [ ] 支持发送历史记录
- [ ] 支持Webhook回调
- [ ] 支持更多消息类型（视频、文件等）

---

## 👥 贡献者

- 开发: Kiro AI Assistant
- 测试: 待补充
- 文档: Kiro AI Assistant

---

## 📄 许可证

MIT License

---

**更新时间**: 2025-02-01
**版本**: v1.1.0
