"""
测试商户服务
"""
import pytest
from app.services.merchant import MerchantService


@pytest.mark.asyncio
async def test_create_merchant(db_session, sample_merchant_data):
    """测试创建商户"""
    service = MerchantService()
    
    merchant = await service.create_merchant(**sample_merchant_data)
    
    assert merchant.id is not None
    assert merchant.telegram_id == sample_merchant_data["telegram_id"]
    assert merchant.merchant_code == sample_merchant_data["merchant_code"]
    assert merchant.is_active is True


@pytest.mark.asyncio
async def test_get_merchant_by_telegram_id(db_session, sample_merchant_data):
    """测试根据Telegram ID获取商户"""
    service = MerchantService()
    
    # 创建商户
    created = await service.create_merchant(**sample_merchant_data)
    
    # 查询商户
    merchant = await service.get_by_telegram_id(sample_merchant_data["telegram_id"])
    
    assert merchant is not None
    assert merchant.id == created.id
    assert merchant.telegram_id == sample_merchant_data["telegram_id"]


@pytest.mark.asyncio
async def test_duplicate_merchant(db_session, sample_merchant_data):
    """测试重复创建商户"""
    service = MerchantService()
    
    # 第一次创建
    await service.create_merchant(**sample_merchant_data)
    
    # 第二次创建应该失败
    with pytest.raises(ValueError):
        await service.create_merchant(**sample_merchant_data)

