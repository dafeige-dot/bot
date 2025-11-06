"""
广播服务
"""
import asyncio
from typing import List, Optional, Dict
from datetime import datetime

from telegram import Bot
from telegram.error import TelegramError
from loguru import logger

from app.models.merchant import Merchant
from app.services.merchant import MerchantService
from app.config import settings


class BroadcastService:
    """广播服务类"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.merchant_service = MerchantService()
    
    async def broadcast_to_all(
        self,
        message: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = True
    ) -> Dict:
        """向所有活跃商户广播消息"""
        
        # 获取所有活跃商户
        merchants = await self.merchant_service.get_all_active_merchants()
        
        return await self.broadcast_to_merchants(
            merchant_ids=[m.id for m in merchants],
            message=message,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )
    
    async def broadcast_to_merchants(
        self,
        merchant_ids: List[int],
        message: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = True
    ) -> Dict:
        """向指定商户列表广播消息"""
        
        total = len(merchant_ids)
        success_count = 0
        failed_count = 0
        failed_merchants = []
        
        logger.info(f"开始广播消息，目标商户数: {total}")
        
        for merchant_id in merchant_ids:
            try:
                # 获取商户
                merchant = await self.merchant_service.get_by_id(merchant_id)
                
                if not merchant:
                    logger.warning(f"商户 {merchant_id} 不存在")
                    failed_count += 1
                    continue
                
                # 发送消息
                await self.bot.send_message(
                    chat_id=merchant.telegram_id,
                    text=message,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview
                )
                
                success_count += 1
                logger.debug(f"消息已发送到商户 {merchant_id}")
                
                # 延迟，避免触发限流
                if settings.BROADCAST_DELAY_MS > 0:
                    await asyncio.sleep(settings.BROADCAST_DELAY_MS / 1000)
                
            except TelegramError as e:
                logger.warning(f"发送消息到商户 {merchant_id} 失败: {e}")
                failed_count += 1
                failed_merchants.append({
                    "merchant_id": merchant_id,
                    "error": str(e)
                })
            except Exception as e:
                logger.error(f"处理商户 {merchant_id} 时出错: {e}")
                failed_count += 1
                failed_merchants.append({
                    "merchant_id": merchant_id,
                    "error": str(e)
                })
        
        result = {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "success_rate": success_count / total if total > 0 else 0,
            "failed_merchants": failed_merchants,
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(
            f"广播完成 - 总计: {total}, 成功: {success_count}, "
            f"失败: {failed_count}, 成功率: {result['success_rate']:.2%}"
        )
        
        return result
    
    async def send_to_merchant(
        self,
        merchant_id: int,
        message: str,
        parse_mode: Optional[str] = None
    ) -> bool:
        """发送消息给单个商户"""
        try:
            merchant = await self.merchant_service.get_by_id(merchant_id)
            
            if not merchant:
                logger.warning(f"商户 {merchant_id} 不存在")
                return False
            
            await self.bot.send_message(
                chat_id=merchant.telegram_id,
                text=message,
                parse_mode=parse_mode
            )
            
            logger.info(f"消息已发送到商户 {merchant_id}")
            return True
            
        except Exception as e:
            logger.error(f"发送消息到商户 {merchant_id} 失败: {e}")
            return False
    
    async def broadcast_with_condition(
        self,
        message: str,
        condition_func,
        parse_mode: Optional[str] = None
    ) -> Dict:
        """根据条件广播消息"""
        
        # 获取所有活跃商户
        merchants = await self.merchant_service.get_all_active_merchants()
        
        # 筛选符合条件的商户
        target_merchants = [m for m in merchants if condition_func(m)]
        
        return await self.broadcast_to_merchants(
            merchant_ids=[m.id for m in target_merchants],
            message=message,
            parse_mode=parse_mode
        )

