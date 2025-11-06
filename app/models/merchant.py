"""
商户模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    Boolean,
    Numeric,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class Merchant(Base):
    """商户模型"""
    
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Telegram信息
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True, comment="Telegram用户ID")
    username = Column(String(255), nullable=True, comment="Telegram用户名")
    first_name = Column(String(255), nullable=True, comment="名字")
    last_name = Column(String(255), nullable=True, comment="姓氏")
    
    # 商户信息
    merchant_code = Column(String(50), nullable=False, index=True, comment="商户编号")
    merchant_name = Column(String(255), nullable=False, comment="商户名称")
    contact_phone = Column(String(50), nullable=True, comment="联系电话")
    contact_email = Column(String(255), nullable=True, comment="联系邮箱")
    
    # 余额信息
    balance = Column(Numeric(15, 2), default=0, nullable=False, comment="可用余额")
    frozen_balance = Column(Numeric(15, 2), default=0, nullable=False, comment="冻结余额")
    total_balance = Column(Numeric(15, 2), default=0, nullable=False, comment="总余额")
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    is_verified = Column(Boolean, default=False, nullable=False, comment="是否已验证")
    
    # 权限
    role = Column(String(50), default="merchant", nullable=False, comment="角色: merchant, admin, super_admin")
    permissions = Column(Text, nullable=True, comment="权限列表(JSON)")
    
    # 其他信息
    language = Column(String(10), default="zh", nullable=False, comment="语言偏好 (zh/en)")
    timezone = Column(String(50), default="Asia/Shanghai", nullable=False, comment="时区")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    last_active_at = Column(DateTime, nullable=True, comment="最后活跃时间")
    
    # 关联关系
    transactions = relationship("Transaction", back_populates="merchant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="merchant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Merchant(id={self.id}, code={self.merchant_code}, name={self.merchant_name})>"
    
    @property
    def full_name(self) -> str:
        """获取完整姓名"""
        parts = [self.first_name, self.last_name]
        return " ".join(filter(None, parts)) or self.username or f"用户{self.telegram_id}"
    
    @property
    def available_balance(self) -> float:
        """可用余额"""
        return float(self.balance or 0)
    
    def update_balance(self, amount: float, frozen: float = 0):
        """更新余额"""
        self.balance += amount
        self.frozen_balance += frozen
        self.total_balance = self.balance + self.frozen_balance
    
    def can_broadcast(self) -> bool:
        """是否可以发送广播"""
        return self.role in ["admin", "super_admin"]

