# 图片识别开关快速参考

## 🎯 核心特性

✨ **会话级别控制** - 每个私聊/群聊独立设置，互不影响

## 🎯 快速开关

### 管理员命令（会话级别）
```bash
# 在需要控制的会话中执行

# 查看当前会话状态
/toggle_ocr

# 开启当前会话的OCR
/toggle_ocr on

# 关闭当前会话的OCR
/toggle_ocr off
```

### 环境变量（全局开关）
```bash
# .env 文件
ENABLE_OCR=true   # 全局开启（推荐）
ENABLE_OCR=false  # 全局关闭（所有会话都无法使用）
```

## 📊 实现方式

✅ **已完成的功能**
- [x] 数据库模型（`merchant.enable_ocr` 字段）
- [x] 数据库迁移脚本
- [x] 会话级别开关控制
- [x] 全局开关支持（`.env`）
- [x] 图片处理器双重检查（`handlers.py`）
- [x] 管理员命令（`/toggle_ocr`）
- [x] 命令注册（`main.py`）
- [x] 帮助文档更新（`/help`）
- [x] 多语言支持（中英文）
- [x] 权限验证（仅管理员）
- [x] 持久化存储（重启后保持）

## 🔄 工作流程

```
用户在会话A发送图片
    ↓
检查是否绑定商户
    ↓
检查全局 ENABLE_OCR（.env配置）
    ↓
检查会话A的 enable_ocr（数据库）
    ↓
├─ 任一关闭 → 提示相应消息
└─ 都开启 → 继续 OCR 识别流程
```

## 💡 典型场景

### 场景1：多会话独立控制
```
群聊A（客服群）：开启 OCR ✅
群聊B（测试群）：关闭 OCR ❌
私聊C（商户1）：开启 OCR ✅
私聊D（商户2）：关闭 OCR ❌
```

### 场景2：临时关闭某个群
```bash
# 在群聊B中执行
/toggle_ocr off  # 只影响群聊B

# 其他会话不受影响
```

## 📝 注意事项

✅ 设置会保存到数据库，重启后依然有效
✅ 每个会话独立设置，互不影响
✅ 新绑定的会话默认开启 OCR
⚠️ 需要先绑定商户才能使用此功能
⚠️ 仅管理员可以切换开关

## 🔗 相关文件

- `app/models/merchant.py` - 数据库模型（enable_ocr字段）
- `migrations/versions/add_enable_ocr_to_merchant.py` - 数据库迁移
- `app/config.py` - 全局配置
- `app/bot/commands.py` - 命令实现
- `app/bot/handlers.py` - 功能检查
- `app/main.py` - 命令注册
- `env.template` - 环境变量模板
- `docs/OCR开关使用说明.md` - 详细文档
