"""
后端 API 客户端
用于调用 Java 后端接口
"""
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from loguru import logger
from app.config import settings


class BackendAPIClient:
    """后端 API 客户端"""
    
    def __init__(self):
        self.base_url = settings.BACKEND_API_URL
        self.timeout = settings.BACKEND_API_TIMEOUT
    
    async def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST 请求"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            logger.info(f"🔗 API 请求开始: {endpoint}, URL: {url}, 参数: {data}")
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, data=data) as response:
                    # 检查 HTTP 状态码
                    if response.status != 200:
                        logger.warning(f"⚠️ API 返回非 200 状态码: {response.status}")
                        text = await response.text()
                        logger.warning(f"响应内容: {text[:200]}")
                        return {
                            "code": response.status,
                            "msg": f"HTTP {response.status}: {text[:100]}"
                        }
                    
                    # 尝试解析 JSON
                    try:
                        result = await response.json()
                        logger.info(f"✅ API 请求成功: {endpoint}, 响应码: {result.get('code', 'N/A')}")
                        logger.debug(f"完整响应: {result}")
                        return result
                    except Exception as json_err:
                        logger.error(f"❌ JSON 解析失败: {json_err}")
                        text = await response.text()
                        logger.error(f"原始响应: {text[:500]}")
                        return {
                            "code": 500,
                            "msg": f"响应格式错误: {str(json_err)}"
                        }
                        
        except aiohttp.ClientConnectorError as e:
            logger.error(f"❌ 连接失败 ({endpoint}): 无法连接到 {url}")
            logger.error(f"详细错误: {e}")
            return {
                "code": 503,
                "msg": f"无法连接到后端服务 ({self.base_url})"
            }
        except (aiohttp.ClientTimeout, asyncio.TimeoutError) as e:
            logger.error(f"⏱️ 请求超时 ({endpoint}): {e}")
            return {
                "code": 504,
                "msg": f"请求超时（超过 {self.timeout} 秒）"
            }
        except asyncio.CancelledError:
            logger.warning(f"⚠️ 请求被取消 ({endpoint})")
            return {
                "code": 499,
                "msg": "请求被取消"
            }
        except aiohttp.ClientError as e:
            logger.error(f"❌ 网络错误 ({endpoint}): {e}")
            return {
                "code": 500,
                "msg": f"网络请求失败: {str(e)}"
            }
        except Exception as e:
            logger.exception(f"💥 API 调用异常 ({endpoint}): {e}")
            return {
                "code": 500,
                "msg": f"系统错误: {str(e)}"
            }
    
    async def query_balance(self, merchant_id: str) -> Dict[str, Any]:
        """
        查询余额
        
        参数:
            merchant_id: 商户号
        
        返回:
            {
                "code": 200,
                "msg": "success",
                "merchant_id": "xxx",
                "balance": "总余额",
                "use_balance": "可用余额",
                "frozen_balance": "冻结余额"
            }
        """
        return await self._post("balance", {"merchant_id": merchant_id})
    
    async def query_order(self, merchant_id: str, order_id: str) -> Dict[str, Any]:
        """
        查询订单
        
        参数:
            merchant_id: 商户号
            order_id: 订单ID（商户订单号）
        
        返回:
            {
                "code": 200,
                "msg": "",
                "type": "payin" 或 "payout",
                "real_pay": "实际支付金额",
                "order_price": "订单金额",
                "order_num": "平台订单号",
                "mch_order_no": "商户订单号",
                "status": 0/1/2/3,
                "status_desc": "状态描述"
            }
        """
        return await self._post("order", {
            "merchant_id": merchant_id,
            "order_id": order_id
        })
    
    async def check_utr(self, merchant_id: str, utr: str) -> Dict[str, Any]:
        """
        查询 UTR
        
        参数:
            merchant_id: 商户号
            utr: UTR
        """
        return await self._post("check_utr", {
            "merchant_id": merchant_id,
            "utr": utr
        })
    
    async def confirm_utr(self, merchant_id: str, utr: str, mer_order_num: str) -> Dict[str, Any]:
        """
        UTR 补单
        
        参数:
            merchant_id: 商户号
            utr: UTR
            mer_order_num: 商户订单号
        """
        return await self._post("confirm_utr", {
            "merchant_id": merchant_id,
            "utr": utr,
            "mer_order_num": mer_order_num
        })
    
    async def check_upi(self, merchant_id: str, upi: str) -> Dict[str, Any]:
        """
        查询 UPI
        
        参数:
            merchant_id: 商户号
            upi: UPI
        
        返回:
            {
                "code": 200,
                "msg": "success",
                "is_upi": 0/1,  # 1表示是我们的UPI，0表示不是
                "data": {...}
            }
        """
        return await self._post("check_upi", {
            "merchant_id": merchant_id,
            "upi": upi
        })
    
    async def query_merchant_success_rate(self, merchant_id: str, time_range: str) -> Dict[str, Any]:
        """
        查询商户成功率
        
        参数:
            merchant_id: 商户号
            time_range: 时间范围 (15m, 1h, d)
        
        返回:
            {
                "code": 200,
                "msg": "success",
                "merchant_id": "xxx",
                "time_range": "15m",
                "total_count": 100,
                "success_count": 95,
                "success_rate": "95.00"
            }
        """
        return await self._post("merchant_success_rate", {
            "merchant_id": merchant_id,
            "time_range": time_range
        })


# 创建全局实例
api_client = BackendAPIClient()

