"""
移除 merchant_code 的唯一约束
允许多个聊天共享同一个商户号
"""
import asyncio
from sqlalchemy import text
from app.database.session import engine


async def fix_unique_constraint():
    """移除 merchant_code 的唯一约束"""
    async with engine.begin() as conn:
        print("正在移除 merchant_code 唯一约束...")
        
        try:
            # 删除唯一约束
            await conn.execute(text(
                "ALTER TABLE merchants DROP CONSTRAINT IF EXISTS ix_merchants_merchant_code;"
            ))
            print("✅ 已删除旧的唯一索引")
        except Exception as e:
            print(f"删除旧索引失败（可能不存在）: {e}")
        
        try:
            # 删除唯一约束（另一种可能的名称）
            await conn.execute(text(
                "ALTER TABLE merchants DROP CONSTRAINT IF EXISTS merchants_merchant_code_key;"
            ))
            print("✅ 已删除唯一约束")
        except Exception as e:
            print(f"删除约束失败（可能不存在）: {e}")
        
        try:
            # 重新创建普通索引（非唯一）
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_merchants_merchant_code ON merchants(merchant_code);"
            ))
            print("✅ 已创建新的普通索引")
        except Exception as e:
            print(f"创建索引失败: {e}")
        
        print("\n✅ 完成！现在可以允许多个聊天共享同一个商户号了。")


if __name__ == "__main__":
    print("=" * 60)
    print("移除 merchant_code 唯一约束工具")
    print("=" * 60)
    print()
    
    asyncio.run(fix_unique_constraint())
    
    print()
    print("请重启 Bot 以应用更改：")
    print("  Windows: start.bat")
    print("  Linux/Mac: bash scripts/start.sh")

