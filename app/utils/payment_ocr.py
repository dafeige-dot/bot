"""
支付图片 OCR 识别工具
专门用于识别支付截图中的金额、UTR、UPI等信息
"""
import re
from typing import Dict, Optional, List
from loguru import logger


class PaymentOCRParser:
    """支付截图 OCR 解析器"""
    
    @staticmethod
    def extract_amount(text: str) -> Optional[str]:
        """
        提取金额
        
        支持格式:
        - ₹500
        - Rs 500
        - 500.00
        """
        patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # ₹500 or ₹1,000.00
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # Rs 500 or Rs. 1,000.00
            r'INR\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # INR 500
            r'(?:^|\s)(\d+(?:,\d+)*(?:\.\d+)?)(?:\s*(?:rupees?|rs|inr))',  # 500 rupees
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                logger.info(f"提取到金额: {amount}")
                return amount
        
        # 尝试查找纯数字（可能是金额）
        # 通常金额在100-999999之间
        numbers = re.findall(r'\b(\d{3,6})\b', text)
        if numbers:
            # 返回最有可能的金额（通常是较大的数字）
            amounts = [n for n in numbers if 100 <= int(n) <= 999999]
            if amounts:
                logger.info(f"推测金额: {amounts[0]}")
                return amounts[0]
        
        return None
    
    @staticmethod
    def extract_utr(text: str) -> Optional[str]:
        """
        提取 UTR (UPI Transaction Reference)
        
        格式:
        - 12位数字
        - 可能包含字母
        例如: 566885730682, 328701234567
        """
        patterns = [
            r'(?:UPI\s+transaction\s+ID|UPI\s+ID|Transaction\s+ID|UTR)[:\s]*([A-Z0-9]{10,15})',
            r'\b([0-9]{12})\b',  # 12位纯数字
            r'\b([0-9]{10,15})\b',  # 10-15位数字
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                utr = match.group(1)
                # UTR 通常是12位数字
                if len(utr) >= 10 and utr.isdigit():
                    logger.info(f"提取到 UTR: {utr}")
                    return utr
        
        return None
    
    @staticmethod
    def extract_upi(text: str) -> Optional[str]:
        """
        提取 UPI ID
        
        格式:
        - xxx@xxx (VPA格式)
        例如: ppqr01.kwjczm@iob, merchant@paytm, user123@ybl
        """
        # UPI VPA 格式: username@bank
        pattern = r'\b([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+)\b'
        
        matches = re.findall(pattern, text)
        if matches:
            # 过滤掉邮箱地址，只保留 UPI
            upis = [m for m in matches if not any(domain in m.lower() for domain in [
                '@gmail', '@yahoo', '@hotmail', '@outlook', '@qq', '@163', '@okaxis'
            ])]
            
            if upis:
                upi = upis[0]
                logger.info(f"提取到 UPI: {upi}")
                return upi
        
        return None
    
    @staticmethod
    def extract_bank_name(text: str) -> Optional[str]:
        """提取银行名称"""
        banks = [
            'State Bank of India', 'SBI',
            'HDFC', 'ICICI', 'Axis Bank',
            'Kotak', 'Yes Bank', 'IDBI',
            'PNB', 'Bank of Baroda', 'Canara Bank',
            'Union Bank', 'Indian Bank', 'Bank of India',
            'Paytm', 'PhonePe', 'Google Pay', 'GPay'
        ]
        
        for bank in banks:
            if bank.lower() in text.lower():
                logger.info(f"识别到银行: {bank}")
                return bank
        
        return None
    
    @staticmethod
    def extract_sender_name(text: str) -> Optional[str]:
        """提取付款人姓名"""
        # 查找 "From: NAME" 或 "Paid by NAME"
        patterns = [
            r'From[:\s]+([A-Z][A-Za-z\s]+?)(?:\(|$|\n)',
            r'Paid\s+by[:\s]+([A-Z][A-Za-z\s]+?)(?:\(|$|\n)',
            r'Sender[:\s]+([A-Z][A-Za-z\s]+?)(?:\(|$|\n)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                logger.info(f"提取到付款人: {name}")
                return name
        
        return None
    
    @classmethod
    def parse(cls, ocr_text: str) -> Dict[str, Optional[str]]:
        """
        解析 OCR 文本，提取所有支付信息
        
        返回:
            {
                'amount': '500',
                'utr': '566885730682',
                'upi': 'ppqr01.kwjczm@iob',
                'bank': 'State Bank of India',
                'sender': 'PRAVIN MANOHAR HARINKHEDE'
            }
        """
        logger.info("开始解析支付截图 OCR 文本")
        
        result = {
            'amount': cls.extract_amount(ocr_text),
            'utr': cls.extract_utr(ocr_text),
            'upi': cls.extract_upi(ocr_text),
            'bank': cls.extract_bank_name(ocr_text),
            'sender': cls.extract_sender_name(ocr_text),
        }
        
        logger.info(f"解析结果: {result}")
        return result


def parse_payment_screenshot(ocr_text: str) -> Dict[str, Optional[str]]:
    """
    解析支付截图 OCR 文本的快捷函数
    
    Args:
        ocr_text: OCR 识别的原始文本
    
    Returns:
        包含 amount, utr, upi, bank, sender 的字典
    """
    return PaymentOCRParser.parse(ocr_text)

