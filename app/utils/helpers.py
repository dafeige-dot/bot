"""
辅助函数模块
"""
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger


def generate_code(length: int = 6) -> str:
    """生成随机验证码"""
    return ''.join(random.choices(string.digits, k=length))


def generate_token(length: int = 32) -> str:
    """生成随机token"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed


def format_amount(amount: float, currency: str = "CNY") -> str:
    """格式化金额"""
    symbols = {
        "CNY": "¥",
        "USD": "$",
        "EUR": "€",
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_datetime(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_order_id(text: str) -> Optional[str]:
    """从文本中解析订单号"""
    import re
    
    # 常见订单号格式
    patterns = [
        r'\b\d{10,20}\b',  # 纯数字订单号
        r'\b[A-Z]{2}\d{8,16}\b',  # 字母+数字
        r'\b\d{4}-\d{4}-\d{4}\b',  # 带分隔符
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None


def validate_image_size(file_size: int, max_size_mb: int = 10) -> bool:
    """验证图片大小"""
    max_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_bytes


def escape_markdown(text: str) -> str:
    """转义Markdown特殊字符"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

