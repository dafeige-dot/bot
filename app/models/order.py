"""
订单模型
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


class Order(Base):
    """订单模型"""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 订单信息
    order_no = Column(String(100), unique=True, nullable=False, index=True, comment="订单号")
    external_order_no = Column(String(100), nullable=True, index=True, comment="外部订单号")
    
    # 商户关联
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True, comment="商户ID")
    
    # 订单详情
    order_type = Column(String(50), nullable=False, comment="订单类型")
    order_status = Column(String(50), default="pending", nullable=False, index=True, comment="订单状态")
    
    # 金额信息
    amount = Column(Numeric(15, 2), nullable=False, comment="订单金额")
    currency = Column(String(10), default="CNY", nullable=False, comment="币种")
    
    # 商品信息
    product_name = Column(String(255), nullable=True, comment="商品名称")
    product_description = Column(Text, nullable=True, comment="商品描述")
    quantity = Column(Integer, default=1, nullable=False, comment="数量")
    
    # 客户信息
    customer_name = Column(String(255), nullable=True, comment="客户姓名")
    customer_phone = Column(String(50), nullable=True, comment="客户电话")
    customer_address = Column(Text, nullable=True, comment="客户地址")
    
    # 支付信息
    payment_method = Column(String(50), nullable=True, comment="支付方式")
    payment_time = Column(DateTime, nullable=True, comment="支付时间")
    payment_status = Column(String(50), default="unpaid", nullable=False, comment="支付状态")
    
    # 物流信息
    shipping_method = Column(String(50), nullable=True, comment="配送方式")
    tracking_no = Column(String(100), nullable=True, comment="物流单号")
    shipping_status = Column(String(50), nullable=True, comment="物流状态")
    
    # OCR相关
    ocr_image_path = Column(String(500), nullable=True, comment="OCR图片路径")
    ocr_text = Column(Text, nullable=True, comment="OCR识别文本")
    ocr_confidence = Column(Numeric(5, 2), nullable=True, comment="OCR置信度")
    
    # 备注
    notes = Column(Text, nullable=True, comment="订单备注")
    merchant_notes = Column(Text, nullable=True, comment="商户备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 关联关系
    merchant = relationship("Merchant", back_populates="orders")
    
    # 索引
    __table_args__ = (
        Index("idx_order_merchant_created", "merchant_id", "created_at"),
        Index("idx_order_status", "order_status", "created_at"),
    )
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_no={self.order_no}, status={self.order_status})>"
    
    @property
    def is_paid(self) -> bool:
        """是否已支付"""
        return self.payment_status == "paid"
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.order_status == "completed"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "order_no": self.order_no,
            "order_type": self.order_type,
            "order_status": self.order_status,
            "amount": float(self.amount),
            "currency": self.currency,
            "product_name": self.product_name,
            "customer_name": self.customer_name,
            "payment_status": self.payment_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

