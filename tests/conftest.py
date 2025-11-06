"""
Pytest配置文件
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.config import settings


# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """创建测试数据库会话"""
    # 创建测试引擎
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def sample_merchant_data():
    """示例商户数据"""
    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "merchant_code": "TEST001",
        "merchant_name": "测试商户",
    }


@pytest.fixture
def sample_order_data():
    """示例订单数据"""
    return {
        "order_type": "purchase",
        "amount": 100.00,
        "product_name": "测试商品",
        "customer_name": "测试客户",
    }

