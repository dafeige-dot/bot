"""
交易记录模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class Transaction(Base):
    """交易记录模型"""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 交易信息
    transaction_no = Column(String(100), unique=True, nullable=False, index=True, comment="交易流水号")
    
    # 商户关联
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True, comment="商户ID")
    
    # 交易类型
    transaction_type = Column(String(50), nullable=False, index=True, comment="交易类型: recharge, withdraw, payment, refund")
    transaction_status = Column(String(50), default="pending", nullable=False, index=True, comment="交易状态: pending, success, failed, cancelled")
    
    # 金额信息
    amount = Column(Numeric(15, 2), nullable=False, comment="交易金额")
    currency = Column(String(10), default="CNY", nullable=False, comment="币种")
    
    # 余额变动
    balance_before = Column(Numeric(15, 2), nullable=False, comment="交易前余额")
    balance_after = Column(Numeric(15, 2), nullable=False, comment="交易后余额")
    
    # 关联订单
    order_id = Column(Integer, nullable=True, comment="关联订单ID")
    order_no = Column(String(100), nullable=True, index=True, comment="关联订单号")
    
    # 交易渠道
    channel = Column(String(50), nullable=True, comment="交易渠道")
    payment_method = Column(String(50), nullable=True, comment="支付方式")
    
    # 第三方信息
    third_party_no = Column(String(100), nullable=True, comment="第三方交易号")
    third_party_response = Column(Text, nullable=True, comment="第三方响应(JSON)")
    
    # 操作人
    operator_id = Column(Integer, nullable=True, comment="操作人ID")
    operator_name = Column(String(255), nullable=True, comment="操作人姓名")
    
    # 描述和备注
    description = Column(String(500), nullable=True, comment="交易描述")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 关联关系
    merchant = relationship("Merchant", back_populates="transactions")
    
    # 索引
    __table_args__ = (
        Index("idx_transaction_merchant_created", "merchant_id", "created_at"),
        Index("idx_transaction_type_status", "transaction_type", "transaction_status"),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, no={self.transaction_no}, type={self.transaction_type}, amount={self.amount})>"
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.transaction_status == "success"
    
    @property
    def is_income(self) -> bool:
        """是否为收入"""
        return self.transaction_type in ["recharge", "refund"]
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "transaction_no": self.transaction_no,
            "transaction_type": self.transaction_type,
            "transaction_status": self.transaction_status,
            "amount": float(self.amount),
            "currency": self.currency,
            "balance_before": float(self.balance_before),
            "balance_after": float(self.balance_after),
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

