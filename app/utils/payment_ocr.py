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
        # 1) 优先匹配带货币符号/关键词的金额（最可靠）
        patterns = [
            r'₹\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'Rs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'INR\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'(?:amount|paid|payment)[:\s]+(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                val = m.group(1).replace(',', '')
                logger.info(f"提取到金额(带符号/关键词): {val}")
                return val

        # 2) 行级启发：在不含日期词的行中查找“独立数字行”
        lines: List[str] = [ln.strip() for ln in text.splitlines() if ln.strip()]
        month_words = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                       'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        candidates: List[float] = []
        for ln in lines:
            ln_low = ln.lower()
            # 排除包含月份/日期的行，避免把年份当金额
            if any(m in ln_low for m in month_words) or re.search(r'\b20\d{2}\b|\b19\d{2}\b', ln_low):
                continue
            # 行内提取数字
            for num in re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b', ln):
                clean = num.replace(',', '')
                try:
                    value = float(clean)
                    # 金额合理区间：1 ~ 1,000,000，且排除明显年份 1900~2099
                    if 1 <= value <= 1_000_000 and not (1900 <= value <= 2099):
                        candidates.append(value)
                except Exception:
                    pass
        if candidates:
            best = str(int(max(candidates))) if max(candidates).is_integer() else str(max(candidates))
            logger.info(f\"启发式金额候选: {best}\")
            return best

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

