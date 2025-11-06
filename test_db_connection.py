#!/usr/bin/env python
"""
测试数据库连接
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("  PostgreSQL 连接测试")
    print("=" * 60)
    print()
    
    # 加载配置
    try:
        from app.config import settings
        print(f"✅ 配置加载成功")
        print(f"数据库URL: {settings.DATABASE_URL}")
        print()
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    # 测试连接
    print("正在测试数据库连接...")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
        )
        
        async with engine.connect() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            
            print("✅ 数据库连接成功！")
            print()
            print(f"PostgreSQL 版本: {version}")
            print()
            
        await engine.dispose()
        
        print("=" * 60)
        print("🎉 连接测试通过！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print()
        print("可能的原因：")
        print("1. PostgreSQL 服务未运行")
        print("2. 数据库不存在或用户权限不足")
        print("3. 主机名/端口配置错误")
        print("4. 用户名或密码错误")
        print()
        print("建议检查：")
        print("1. 运行: Get-Service postgresql*")
        print("2. 使用 127.0.0.1 而不是 localhost")
        print("3. 确认数据库和用户已创建")
        print()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

