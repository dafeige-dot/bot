"""
余额服务
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy import select, desc
from decimal import Decimal

from app.models.merchant import Merchant
from app.models.transaction import Transaction
from app.database.session import AsyncSessionLocal
from app.utils.helpers import generate_token, format_datetime
from loguru import logger


class BalanceService:
    """余额服务类"""
    
    async def get_balance(self, merchant_id: int) -> Dict:
        """获取余额信息"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            merchant = result.scalar_one_or_none()
            
            if not merchant:
                raise ValueError("商户不存在")
            
            return {
                "available": float(merchant.balance or 0),
                "frozen": float(merchant.frozen_balance or 0),
                "total": float(merchant.total_balance or 0),
                "query_time": format_datetime(),
            }
    
    async def add_balance(
        self,
        merchant_id: int,
        amount: float,
        transaction_type: str = "recharge",
        description: str = "充值",
        order_no: Optional[str] = None,
    ) -> Transaction:
        """增加余额"""
        if amount <= 0:
            raise ValueError("金额必须大于0")
        
        async with AsyncSessionLocal() as session:
            # 获取商户
            result = await session.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            merchant = result.scalar_one_or_none()
            
            if not merchant:
                raise ValueError("商户不存在")
            
            # 记录变动前余额
            balance_before = float(merchant.balance)
            
            # 更新余额
            merchant.balance += Decimal(str(amount))
            merchant.total_balance = merchant.balance + merchant.frozen_balance
            
            balance_after = float(merchant.balance)
            
            # 创建交易记录
            transaction = Transaction(
                transaction_no=self._generate_transaction_no(),
                merchant_id=merchant_id,
                transaction_type=transaction_type,
                transaction_status="success",
                amount=Decimal(str(amount)),
                balance_before=Decimal(str(balance_before)),
                balance_after=Decimal(str(balance_after)),
                order_no=order_no,
                description=description,
                completed_at=datetime.utcnow(),
            )
            
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            
            logger.info(
                f"商户 {merchant_id} 余额增加: ¥{amount}, "
                f"余额: {balance_before} -> {balance_after}"
            )
            
            return transaction
    
    async def deduct_balance(
        self,
        merchant_id: int,
        amount: float,
        transaction_type: str = "payment",
        description: str = "支付",
        order_no: Optional[str] = None,
    ) -> Transaction:
        """扣减余额"""
        if amount <= 0:
            raise ValueError("金额必须大于0")
        
        async with AsyncSessionLocal() as session:
            # 获取商户
            result = await session.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            merchant = result.scalar_one_or_none()
            
            if not merchant:
                raise ValueError("商户不存在")
            
            # 检查余额
            if float(merchant.balance) < amount:
                raise ValueError("余额不足")
            
            # 记录变动前余额
            balance_before = float(merchant.balance)
            
            # 更新余额
            merchant.balance -= Decimal(str(amount))
            merchant.total_balance = merchant.balance + merchant.frozen_balance
            
            balance_after = float(merchant.balance)
            
            # 创建交易记录
            transaction = Transaction(
                transaction_no=self._generate_transaction_no(),
                merchant_id=merchant_id,
                transaction_type=transaction_type,
                transaction_status="success",
                amount=Decimal(str(amount)),
                balance_before=Decimal(str(balance_before)),
                balance_after=Decimal(str(balance_after)),
                order_no=order_no,
                description=description,
                completed_at=datetime.utcnow(),
            )
            
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            
            logger.info(
                f"商户 {merchant_id} 余额扣减: ¥{amount}, "
                f"余额: {balance_before} -> {balance_after}"
            )
            
            return transaction
    
    async def freeze_balance(
        self,
        merchant_id: int,
        amount: float,
        description: str = "冻结"
    ):
        """冻结余额"""
        if amount <= 0:
            raise ValueError("金额必须大于0")
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            merchant = result.scalar_one_or_none()
            
            if not merchant:
                raise ValueError("商户不存在")
            
            # 检查可用余额
            if float(merchant.balance) < amount:
                raise ValueError("可用余额不足")
            
            # 冻结
            merchant.balance -= Decimal(str(amount))
            merchant.frozen_balance += Decimal(str(amount))
            
            await session.commit()
            
            logger.info(f"商户 {merchant_id} 冻结余额: ¥{amount}")
    
    async def unfreeze_balance(
        self,
        merchant_id: int,
        amount: float,
        description: str = "解冻"
    ):
        """解冻余额"""
        if amount <= 0:
            raise ValueError("金额必须大于0")
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            merchant = result.scalar_one_or_none()
            
            if not merchant:
                raise ValueError("商户不存在")
            
            # 检查冻结余额
            if float(merchant.frozen_balance) < amount:
                raise ValueError("冻结余额不足")
            
            # 解冻
            merchant.frozen_balance -= Decimal(str(amount))
            merchant.balance += Decimal(str(amount))
            
            await session.commit()
            
            logger.info(f"商户 {merchant_id} 解冻余额: ¥{amount}")
    
    async def get_transaction_history(
        self,
        merchant_id: int,
        limit: int = 10,
        transaction_type: Optional[str] = None
    ) -> List[Dict]:
        """获取交易历史"""
        async with AsyncSessionLocal() as session:
            query = select(Transaction).where(
                Transaction.merchant_id == merchant_id
            )
            
            if transaction_type:
                query = query.where(Transaction.transaction_type == transaction_type)
            
            query = query.order_by(desc(Transaction.created_at)).limit(limit)
            
            result = await session.execute(query)
            transactions = result.scalars().all()
            
            return [trans.to_dict() for trans in transactions]
    
    def _generate_transaction_no(self) -> str:
        """生成交易流水号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = generate_token(8)
        return f"TXN{timestamp}{random_str}"

