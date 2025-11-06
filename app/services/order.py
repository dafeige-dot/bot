"""
订单服务
"""
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import select, desc, or_
from decimal import Decimal

from app.models.order import Order
from app.database.session import AsyncSessionLocal
from app.utils.helpers import generate_token
from loguru import logger


class OrderService:
    """订单服务类"""
    
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Order).where(Order.id == order_id)
            )
            return result.scalar_one_or_none()
    
    async def get_by_order_no(self, order_no: str) -> Optional[Order]:
        """根据订单号获取订单"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Order).where(Order.order_no == order_no)
            )
            return result.scalar_one_or_none()
    
    async def search_orders(
        self,
        merchant_id: int,
        keyword: str
    ) -> List[Order]:
        """搜索订单"""
        async with AsyncSessionLocal() as session:
            query = select(Order).where(
                Order.merchant_id == merchant_id,
                or_(
                    Order.order_no.contains(keyword),
                    Order.external_order_no.contains(keyword),
                    Order.customer_name.contains(keyword),
                    Order.customer_phone.contains(keyword)
                )
            )
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_merchant_orders(
        self,
        merchant_id: int,
        page: int = 1,
        page_size: int = 10,
        order_status: Optional[str] = None
    ) -> Dict:
        """获取商户订单列表"""
        async with AsyncSessionLocal() as session:
            query = select(Order).where(Order.merchant_id == merchant_id)
            
            if order_status:
                query = query.where(Order.order_status == order_status)
            
            query = query.order_by(desc(Order.created_at))
            
            # 总数
            total_result = await session.execute(query)
            total = len(total_result.scalars().all())
            
            # 分页
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            
            result = await session.execute(query)
            orders = result.scalars().all()
            
            return {
                "items": [order.to_dict() for order in orders],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
    
    async def create_order(
        self,
        merchant_id: int,
        order_type: str,
        amount: float,
        **kwargs
    ) -> Order:
        """创建订单"""
        async with AsyncSessionLocal() as session:
            order = Order(
                order_no=self._generate_order_no(),
                merchant_id=merchant_id,
                order_type=order_type,
                amount=Decimal(str(amount)),
                order_status="pending",
                payment_status="unpaid",
                **kwargs
            )
            
            session.add(order)
            await session.commit()
            await session.refresh(order)
            
            logger.info(f"创建订单: {order.order_no}, 金额: ¥{amount}")
            
            return order
    
    async def update_order_status(
        self,
        order_id: int,
        order_status: str,
        payment_status: Optional[str] = None
    ) -> Optional[Order]:
        """更新订单状态"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            
            if not order:
                return None
            
            order.order_status = order_status
            
            if payment_status:
                order.payment_status = payment_status
            
            if order_status == "completed":
                order.completed_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(order)
            
            logger.info(f"更新订单状态: {order.order_no} -> {order_status}")
            
            return order
    
    async def add_ocr_result(
        self,
        order_id: int,
        ocr_text: str,
        ocr_confidence: float,
        image_path: str
    ):
        """添加OCR识别结果"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            
            if order:
                order.ocr_text = ocr_text
                order.ocr_confidence = Decimal(str(ocr_confidence))
                order.ocr_image_path = image_path
                
                await session.commit()
    
    def _generate_order_no(self) -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = generate_token(6)
        return f"ORD{timestamp}{random_str}"
    
    async def get_order_statistics(
        self,
        merchant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """获取订单统计"""
        async with AsyncSessionLocal() as session:
            query = select(Order)
            
            if merchant_id:
                query = query.where(Order.merchant_id == merchant_id)
            
            if start_date:
                query = query.where(Order.created_at >= start_date)
            
            if end_date:
                query = query.where(Order.created_at <= end_date)
            
            result = await session.execute(query)
            orders = result.scalars().all()
            
            total_count = len(orders)
            total_amount = sum(float(order.amount) for order in orders)
            
            status_count = {}
            for order in orders:
                status = order.order_status
                status_count[status] = status_count.get(status, 0) + 1
            
            return {
                "total_count": total_count,
                "total_amount": total_amount,
                "status_count": status_count,
                "avg_amount": total_amount / total_count if total_count > 0 else 0
            }

