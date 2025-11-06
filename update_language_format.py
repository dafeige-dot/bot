"""
更新语言格式从 zh-CN 到 zh
"""
import asyncio
from sqlalchemy import text
from app.database.session import engine
from loguru import logger


async def update_language_format():
    """更新语言格式"""
    try:
        async with engine.begin() as conn:
            # 更新 zh-CN 为 zh
            result = await conn.execute(text("""
                UPDATE merchants 
                SET language = 'zh' 
                WHERE language = 'zh-CN';
            """))
            
            logger.info(f"✅ 更新了 {result.rowcount} 条记录: zh-CN -> zh")
            
            # 更新 en-US 为 en (如果存在)
            result = await conn.execute(text("""
                UPDATE merchants 
                SET language = 'en' 
                WHERE language LIKE 'en%';
            """))
            
            if result.rowcount > 0:
                logger.info(f"✅ 更新了 {result.rowcount} 条记录: en-* -> en")
            
    except Exception as e:
        logger.error(f"❌ 更新失败: {e}")
        raise


async def main():
    """主函数"""
    logger.info("开始更新语言格式...")
    await update_language_format()
    logger.info("更新完成！")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())


