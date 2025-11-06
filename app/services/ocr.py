"""
OCR识别服务
"""
import re
from typing import Dict, List, Optional
from pathlib import Path

from loguru import logger
from app.config import settings
from app.utils.helpers import parse_order_id


class OCRService:
    """OCR服务类"""
    
    def __init__(self):
        self.engine = settings.OCR_ENGINE
        self._ocr_instance = None
    
    def _get_paddleocr(self):
        """获取PaddleOCR实例"""
        if self._ocr_instance is None:
            try:
                from paddleocr import PaddleOCR
                
                self._ocr_instance = PaddleOCR(
                    use_angle_cls=True,
                    lang=settings.PADDLEOCR_LANG,
                    use_gpu=settings.PADDLEOCR_USE_GPU,
                    show_log=False
                )
                
                logger.info("PaddleOCR初始化成功")
            except Exception as e:
                logger.error(f"PaddleOCR初始化失败: {e}")
                raise
        
        return self._ocr_instance
    
    async def recognize_order_image(self, image_path: str) -> Dict:
        """识别订单图片"""
        try:
            if not Path(image_path).exists():
                return {
                    "success": False,
                    "error": "图片文件不存在"
                }
            
            # 根据引擎选择识别方法
            if self.engine == "paddleocr":
                result = await self._recognize_with_paddleocr(image_path)
            elif self.engine == "tesseract":
                result = await self._recognize_with_tesseract(image_path)
            elif self.engine == "rapidocr":
                result = await self._recognize_with_rapidocr(image_path)
            elif self.engine == "aliyun":
                result = await self._recognize_with_aliyun(image_path)
            elif self.engine == "tencentcloud":
                result = await self._recognize_with_tencent(image_path)
            elif self.engine == "baidu":
                result = await self._recognize_with_baidu(image_path)
            else:
                return {
                    "success": False,
                    "error": f"不支持的OCR引擎: {self.engine}"
                }
            
            if result["success"]:
                # 提取订单号
                order_numbers = self._extract_order_numbers(result["text"])
                result["order_numbers"] = order_numbers
            
            return result
            
        except Exception as e:
            logger.exception(f"OCR识别出错: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _recognize_with_paddleocr(self, image_path: str) -> Dict:
        """使用PaddleOCR识别"""
        try:
            ocr = self._get_paddleocr()
            
            # 执行OCR
            result = ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return {
                    "success": False,
                    "error": "未识别到文本"
                }
            
            # 提取文本和置信度
            texts = []
            confidences = []
            
            for line in result[0]:
                if line:
                    text = line[1][0]
                    confidence = line[1][1]
                    texts.append(text)
                    confidences.append(confidence)
            
            full_text = "\n".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            logger.info(f"PaddleOCR识别成功, 置信度: {avg_confidence:.2f}")
            
            return {
                "success": True,
                "text": full_text,
                "confidence": avg_confidence,
                "lines": texts,
                "engine": "paddleocr"
            }
            
        except Exception as e:
            logger.error(f"PaddleOCR识别失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _recognize_with_rapidocr(self, image_path: str) -> Dict:
        """使用 RapidOCR (onnxruntime) 识别（纯本地，精度高于 tesseract）"""
        try:
            from rapidocr_onnxruntime import RapidOCR
            ocr = RapidOCR()  # 默认会下载模型到本地缓存
            res, _ = ocr(image_path)
            if not res:
                return {
                    "success": False,
                    "error": "未识别到文本"
                }
            # res: list of [boxes, text, score]
            lines = [item[1] for item in res if len(item) >= 2 and item[1]]
            full_text = "\n".join(lines)
            return {
                "success": True,
                "text": full_text,
                "confidence": None,
                "lines": lines,
                "engine": "rapidocr"
            }
        except Exception as e:
            logger.error(f"RapidOCR 识别失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _recognize_with_tesseract(self, image_path: str) -> Dict:
        """使用 Tesseract 识别（Linux 方案）"""
        try:
            # 延迟导入，避免在未安装时引起 ImportError
            import pytesseract
            from PIL import Image

            # 语言映射：默认为英文，中文使用简体包
            lang_cfg = settings.PADDLEOCR_LANG.lower() if settings.PADDLEOCR_LANG else "eng"
            if lang_cfg.startswith("ch"):
                tess_lang = "chi_sim"
            elif lang_cfg.startswith("en"):
                tess_lang = "eng"
            else:
                tess_lang = "eng"

            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang=tess_lang)

            # Tesseract 没有置信度统一输出，这里简单返回
            full_text = text.strip()
            if not full_text:
                return {
                    "success": False,
                    "error": "未识别到文本"
                }

            logger.info("Tesseract 识别成功")
            return {
                "success": True,
                "text": full_text,
                "confidence": None,
                "lines": [line for line in full_text.splitlines() if line.strip()],
                "engine": "tesseract"
            }
        except Exception as e:
            logger.error(f"Tesseract 识别失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _recognize_with_aliyun(self, image_path: str) -> Dict:
        """使用阿里云OCR识别"""
        # TODO: 实现阿里云OCR
        return {
            "success": False,
            "error": "阿里云OCR暂未实现"
        }
    
    async def _recognize_with_tencent(self, image_path: str) -> Dict:
        """使用腾讯云OCR识别"""
        try:
            import base64
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.ocr.v20181119 import ocr_client, models

            # 读取图片为 base64
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")

            # 凭证与客户端
            cred = credential.Credential(settings.TENCENT_SECRET_ID, settings.TENCENT_SECRET_KEY)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            region = settings.TENCENT_OCR_REGION or "ap-guangzhou"
            client = ocr_client.OcrClient(cred, region, clientProfile)

            # 通用印刷体识别
            req = models.GeneralBasicOCRRequest()
            req.ImageBase64 = img_b64
            # 自动语言
            req.LanguageType = "auto"

            resp = client.GeneralBasicOCR(req)
            # 拼接文本
            lines = [item.DetectedText for item in resp.TextDetections] if getattr(resp, "TextDetections", None) else []
            full_text = "\n".join(lines)

            if not full_text.strip():
                return {
                    "success": False,
                    "error": "未识别到文本"
                }

            logger.info("腾讯云OCR识别成功")
            return {
                "success": True,
                "text": full_text,
                "confidence": None,
                "lines": lines,
                "engine": "tencentcloud"
            }
        except Exception as e:
            logger.error(f"腾讯云OCR识别失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _recognize_with_baidu(self, image_path: str) -> Dict:
        """使用百度OCR识别"""
        # TODO: 实现百度OCR
        return {
            "success": False,
            "error": "百度OCR暂未实现"
        }
    
    def _extract_order_numbers(self, text: str) -> List[str]:
        """从文本中提取订单号"""
        order_numbers = []
        
        # 常见订单号模式
        patterns = [
            r'\b\d{10,20}\b',  # 纯数字订单号 10-20位
            r'\b[A-Z]{2,4}\d{8,16}\b',  # 字母+数字
            r'\b\d{4}[-_]\d{4}[-_]\d{4,8}\b',  # 带分隔符
            r'订单号[:：\s]*([A-Za-z0-9\-_]{8,30})',  # 明确标注的订单号
            r'单号[:：\s]*([A-Za-z0-9\-_]{8,30})',
            r'order[:：\s]*([A-Za-z0-9\-_]{8,30})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # 如果是元组，取第一个元素
                order_no = match[0] if isinstance(match, tuple) else match
                order_no = order_no.strip()
                
                # 验证订单号
                if self._is_valid_order_number(order_no):
                    if order_no not in order_numbers:
                        order_numbers.append(order_no)
        
        logger.info(f"提取到 {len(order_numbers)} 个订单号: {order_numbers}")
        
        return order_numbers
    
    def _is_valid_order_number(self, order_no: str) -> bool:
        """验证订单号是否有效"""
        # 基本规则
        if len(order_no) < 8 or len(order_no) > 30:
            return False
        
        # 排除一些明显不是订单号的情况
        invalid_patterns = [
            r'^\d{4}[-_]\d{2}[-_]\d{2}$',  # 日期格式
            r'^[0-9.]+$',  # 纯数字和点（可能是金额）
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, order_no):
                return False
        
        return True
    
    async def batch_recognize(self, image_paths: List[str]) -> List[Dict]:
        """批量识别"""
        results = []
        
        for image_path in image_paths:
            result = await self.recognize_order_image(image_path)
            results.append({
                "image_path": image_path,
                "result": result
            })
        
        return results

