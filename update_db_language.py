"""
数据库添加语言字段的脚本
直接更新现有数据库，无需 Alembic 迁移
"""
import asyncio
from sqlalchemy import text
from app.database.session import engine
from loguru import logger


async def add_language_column():
    """为 merchants 表添加 language 列"""
    try:
        async with engine.begin() as conn:
            # 检查列是否已存在
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='merchants' AND column_name='language';
            """))
            
            exists = result.fetchone()
            
            if exists:
                logger.info("✅ language 列已存在，跳过")
                return
            
            # 添加列
            await conn.execute(text("""
                ALTER TABLE merchants 
                ADD COLUMN language VARCHAR(10) DEFAULT 'zh' NOT NULL;
            """))
            
            # 添加注释
            await conn.execute(text("""
                COMMENT ON COLUMN merchants.language IS '用户语言偏好 (zh/en)';
            """))
            
            logger.info("✅ 成功添加 language 列到 merchants 表")
            
    except Exception as e:
        logger.error(f"❌ 添加语言列失败: {e}")
        raise


async def main():
    """主函数"""
    logger.info("开始更新数据库...")
    await add_language_column()
    logger.info("数据库更新完成！")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())


