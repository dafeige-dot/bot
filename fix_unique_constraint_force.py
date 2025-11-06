"""
强制移除 merchant_code 的唯一约束
"""
import asyncio
from sqlalchemy import text
from app.database.session import engine


async def list_constraints():
    """列出所有约束"""
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT conname, contype 
            FROM pg_constraint 
            WHERE conrelid = 'merchants'::regclass;
        """))
        
        print("当前约束列表：")
        for row in result:
            print(f"  - {row[0]} (类型: {row[1]})")


async def list_indexes():
    """列出所有索引"""
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'merchants';
        """))
        
        print("\n当前索引列表：")
        for row in result:
            print(f"  - {row[0]}")
            print(f"    {row[1]}")


async def force_fix():
    """强制修复"""
    async with engine.begin() as conn:
        print("\n开始强制修复...\n")
        
        # 1. 删除所有可能的唯一约束
        constraints_to_remove = [
            "ix_merchants_merchant_code",
            "merchants_merchant_code_key",
            "uq_merchants_merchant_code",
        ]
        
        for constraint in constraints_to_remove:
            try:
                await conn.execute(text(
                    f"ALTER TABLE merchants DROP CONSTRAINT IF EXISTS {constraint};"
                ))
                print(f"✅ 尝试删除约束: {constraint}")
            except Exception as e:
                print(f"⚠️  删除约束 {constraint} 失败: {e}")
        
        # 2. 删除所有可能的唯一索引
        indexes_to_remove = [
            "ix_merchants_merchant_code",
            "idx_merchants_merchant_code",
        ]
        
        for index in indexes_to_remove:
            try:
                await conn.execute(text(
                    f"DROP INDEX IF EXISTS {index};"
                ))
                print(f"✅ 尝试删除索引: {index}")
            except Exception as e:
                print(f"⚠️  删除索引 {index} 失败: {e}")
        
        # 3. 创建新的非唯一索引
        try:
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_merchant_code ON merchants(merchant_code);"
            ))
            print(f"✅ 创建新的普通索引: idx_merchant_code")
        except Exception as e:
            print(f"⚠️  创建索引失败: {e}")


async def main():
    print("=" * 70)
    print("强制移除 merchant_code 唯一约束工具")
    print("=" * 70)
    
    # 显示当前状态
    print("\n【修复前】")
    await list_constraints()
    await list_indexes()
    
    # 执行修复
    await force_fix()
    
    # 显示修复后状态
    print("\n" + "=" * 70)
    print("【修复后】")
    await list_constraints()
    await list_indexes()
    
    print("\n" + "=" * 70)
    print("✅ 完成！")
    print("=" * 70)
    print("\n请重启 Bot：")
    print("  start.bat")


if __name__ == "__main__":
    asyncio.run(main())

