"""
商户服务
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant
from app.database.session import AsyncSessionLocal
from app.utils.helpers import generate_token
from loguru import logger


class MerchantService:
    """商户服务类"""
    
    async def get_by_id(self, merchant_id: int) -> Optional[Merchant]:
        """根据ID获取商户"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            return result.scalar_one_or_none()
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Merchant]:
        """根据Telegram ID获取商户"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    async def get_by_merchant_code(self, merchant_code: str) -> Optional[Merchant]:
        """根据商户编号获取商户"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.merchant_code == merchant_code)
            )
            return result.scalar_one_or_none()
    
    async def create_merchant(
        self,
        telegram_id: int,
        merchant_code: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        merchant_name: Optional[str] = None,
    ) -> Merchant:
        """创建商户"""
        async with AsyncSessionLocal() as session:
            # 检查是否已存在
            existing = await session.execute(
                select(Merchant).where(Merchant.telegram_id == telegram_id)
            )
            if existing.scalar_one_or_none():
                raise ValueError("该Telegram账号已注册")
            
            # 创建商户
            merchant = Merchant(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                merchant_code=merchant_code,
                merchant_name=merchant_name or f"商户{merchant_code}",
                balance=0,
                frozen_balance=0,
                total_balance=0,
                is_active=True,
                is_verified=False,
            )
            
            session.add(merchant)
            await session.commit()
            await session.refresh(merchant)
            
            logger.info(f"创建商户成功: {merchant.id} - {merchant.merchant_name}")
            
            return merchant
    
    async def update_merchant(
        self,
        merchant_id: int,
        **kwargs
    ) -> Optional[Merchant]:
        """更新商户信息"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            merchant = result.scalar_one_or_none()
            
            if not merchant:
                return None
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(merchant, key):
                    setattr(merchant, key, value)
            
            merchant.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(merchant)
            
            logger.info(f"更新商户信息: {merchant.id}")
            
            return merchant
    
    async def update_last_active(self, merchant_id: int):
        """更新最后活跃时间"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            merchant = result.scalar_one_or_none()
            
            if merchant:
                merchant.last_active_at = datetime.utcnow()
                await session.commit()
    
    async def get_all_active_merchants(self) -> List[Merchant]:
        """获取所有活跃商户"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.is_active == True)
            )
            return result.scalars().all()
    
    async def get_merchant_list(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None
    ) -> dict:
        """获取商户列表（分页）"""
        async with AsyncSessionLocal() as session:
            query = select(Merchant)
            
            if is_active is not None:
                query = query.where(Merchant.is_active == is_active)
            
            # 总数
            total_result = await session.execute(query)
            total = len(total_result.scalars().all())
            
            # 分页
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            
            result = await session.execute(query)
            merchants = result.scalars().all()
            
            return {
                "items": merchants,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }

