# 数据库设置指南

## 🎉 好消息：数据库连接成功！

如果你看到错误 `relation "idx_merchant_created" already exists`，说明：
- ✅ 数据库连接正常
- ✅ PostgreSQL 配置成功
- ⚠️ 表结构有冲突（之前运行过初始化）

## 🔧 解决方案（3选1）

### 方案 1：删除重建（最快，5秒）⭐推荐

**运行重置脚本：**
```bash
.\reset_db.bat
```

**然后启动 Bot：**
```bash
python app/main.py
```

---

### 方案 2：直接启动（已修复代码）⭐⭐推荐

我已经修复了代码，添加了 `checkfirst=True` 参数，现在可以直接启动：

```bash
python app/main.py
```

如果还有错误，使用方案 1 或 3。

---

### 方案 3：使用 Alembic（专业方式）

#### 步骤 1: 清理现有表（可选）
```bash
.\reset_db.bat
```

#### 步骤 2: 使用 Alembic 迁移
```bash
# 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

#### 或运行自动化脚本：
```bash
.\init_alembic.bat
```

---

## 📊 推荐流程

### 快速测试（开发环境）：

```bash
# 方法 A：重置数据库
.\reset_db.bat
python app/main.py

# 方法 B：直接启动（代码已修复）
python app/main.py
```

### 生产环境部署：

```bash
# 使用 Alembic 进行版本管理
alembic upgrade head
python app/main.py
```

---

## 🔍 验证数据库

### 连接测试：
```bash
python test_db_connection.py
```

### 查看表结构：
```bash
# 使用 psql
D:\soft\pgsql\bin\psql.exe -U merchant_user -h 127.0.0.1 -d merchant_bot_db

# 在 psql 中执行：
\dt              # 查看所有表
\d merchants     # 查看 merchants 表结构
\di              # 查看所有索引
```

### 查看现有索引：
```sql
SELECT indexname, tablename FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;
```

---

## ❓ 常见问题

### Q: 为什么会出现索引重复？
A: 之前运行过 `python app/main.py`，部分表已创建，再次运行时冲突。

### Q: 删除数据库会丢失数据吗？
A: 是的，但开发阶段没有重要数据，可以安全删除。

### Q: 生产环境如何处理？
A: 生产环境使用 Alembic 进行迁移，不要直接删除数据库。

### Q: Alembic 是什么？
A: 数据库版本管理工具，类似 Git，可以追踪数据库结构变更。

---

## ✅ 成功标志

启动 Bot 时应该看到：
```
✓ 数据库连接正常
✓ 数据库表创建成功
✓ Bot初始化完成，开始运行...
```

---

## 🚀 完整启动流程

```bash
# 1. 重置数据库（如果需要）
.\reset_db.bat

# 2. 检查配置
python check_config.py

# 3. 测试连接
python test_db_connection.py

# 4. 启动 Bot
python app/main.py
```

---

## 💡 提示

- ✅ 开发阶段：直接删除重建最快
- ✅ 生产环境：使用 Alembic 迁移
- ✅ 数据重要：先备份再操作
- ✅ 团队协作：用 Alembic 版本管理

