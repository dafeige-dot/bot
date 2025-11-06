# 使用 SQLite 数据库（快速开始）

## 为什么选择 SQLite？

- ✅ 无需安装数据库服务器
- ✅ 零配置，开箱即用
- ✅ 完美适合开发和测试
- ✅ 数据存储在单个文件中

## 快速配置

### 1. 安装 SQLite 驱动

```bash
pip install aiosqlite
```

### 2. 修改 .env 文件

打开 `.env` 文件，将数据库URL改为：

```env
# 使用 SQLite（开发环境）
DATABASE_URL=sqlite+aiosqlite:///./merchant_bot.db
```

### 3. 启动 Bot

```bash
python app/main.py
```

就这么简单！数据库文件会自动创建在项目目录。

## 数据库文件位置

- 数据库文件：`merchant_bot.db`
- 位于项目根目录

## 注意事项

### SQLite vs PostgreSQL

| 特性 | SQLite | PostgreSQL |
|------|--------|------------|
| 安装 | 无需安装 | 需要安装服务器 |
| 配置 | 零配置 | 需要配置 |
| 并发 | 有限 | 优秀 |
| 适用场景 | 开发/测试 | 生产环境 |
| 数据量 | 小到中等 | 大规模 |

### 迁移到 PostgreSQL

当你需要切换到生产环境时：

1. 安装 PostgreSQL
2. 修改 `.env` 中的 `DATABASE_URL`
3. 运行迁移：`alembic upgrade head`

## 完整配置示例

```env
# 开发环境（SQLite）
DATABASE_URL=sqlite+aiosqlite:///./merchant_bot.db

# 生产环境（PostgreSQL）
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname

# 其他配置保持不变...
```

## 常见问题

### Q: SQLite 能用于生产环境吗？
A: 可以，但不推荐。中小规模可以，大规模建议用 PostgreSQL。

### Q: 如何查看 SQLite 数据库？
A: 使用 DB Browser for SQLite 或其他工具。

### Q: SQLite 数据库如何备份？
A: 直接复制 `merchant_bot.db` 文件即可。

