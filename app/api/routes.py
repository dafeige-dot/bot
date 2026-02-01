"""
API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional
from loguru import logger

from app.config import settings
from app.services.merchant import MerchantService
from telegram import Bot


# 创建路由器
router = APIRouter(prefix="/api/v1", tags=["broadcast"])


# 请求模型
class BroadcastRequest(BaseModel):
    """定向广播请求"""
    group_ids: List[int] = Field(..., description="目标群组ID列表（telegram_id）")
    message: Optional[str] = Field(None, description="文本消息内容")
    photo_url: Optional[str] = Field(None, description="图片URL（与message二选一或同时使用）")
    caption: Optional[str] = Field(None, description="图片说明文字")
    
    class Config:
        json_schema_extra = {
            "example": {
                "group_ids": [-1001234567890, -1009876543210],
                "message": "📢 系统通知：今晚22:00进行系统维护",
                "photo_url": None,
                "caption": None
            }
        }


class BroadcastResponse(BaseModel):
    """广播响应"""
    success: bool
    message: str
    total: int
    success_count: int
    failed_count: int
    failed_groups: List[dict] = []


# API密钥验证
async def verify_api_key(x_api_key: str = Header(..., description="API密钥")):
    """验证API密钥"""
    if not settings.API_SECRET_KEY:
        raise HTTPException(status_code=500, detail="服务器未配置API密钥")
    
    if x_api_key != settings.API_SECRET_KEY:
        logger.warning(f"API密钥验证失败: {x_api_key[:10]}...")
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    return True


@router.post("/broadcast/groups", response_model=BroadcastResponse)
async def broadcast_to_groups(
    request: BroadcastRequest,
    _: bool = Depends(verify_api_key)
):
    """
    定向群组广播接口
    
    - **group_ids**: 目标群组的Telegram ID列表（负数）
    - **message**: 文本消息内容（可选）
    - **photo_url**: 图片URL（可选）
    - **caption**: 图片说明（可选）
    
    注意：message 和 photo_url 至少提供一个
    """
    
    # 验证参数
    if not request.message and not request.photo_url:
        raise HTTPException(status_code=400, detail="message 和 photo_url 至少提供一个")
    
    if not request.group_ids:
        raise HTTPException(status_code=400, detail="group_ids 不能为空")
    
    # 验证群组是否存在
    merchant_service = MerchantService()
    merchants = await merchant_service.get_all_active_merchants()
    valid_group_ids = {m.telegram_id for m in merchants if m.telegram_id < 0}
    
    # 过滤出有效的群组ID
    target_groups = [gid for gid in request.group_ids if gid in valid_group_ids]
    invalid_groups = [gid for gid in request.group_ids if gid not in valid_group_ids]
    
    if not target_groups:
        raise HTTPException(
            status_code=404,
            detail=f"所有群组ID都无效或未绑定。无效ID: {invalid_groups}"
        )
    
    logger.info(f"API广播请求: 目标群组 {len(target_groups)} 个")
    
    # 创建Bot实例
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    success_count = 0
    failed_count = 0
    failed_groups = []
    
    # 执行广播
    for group_id in target_groups:
        try:
            if request.photo_url:
                # 发送图片
                await bot.send_photo(
                    chat_id=group_id,
                    photo=request.photo_url,
                    caption=request.caption or request.message
                )
            else:
                # 发送文本
                await bot.send_message(
                    chat_id=group_id,
                    text=request.message
                )
            
            success_count += 1
            logger.info(f"发送成功: 群组 {group_id}")
            
            # 延迟避免限流
            if settings.BROADCAST_DELAY_MS > 0:
                import asyncio
                await asyncio.sleep(settings.BROADCAST_DELAY_MS / 1000)
                
        except Exception as e:
            failed_count += 1
            error_msg = str(e)[:100]
            logger.error(f"发送失败: 群组 {group_id}, 错误: {error_msg}")
            failed_groups.append({
                "group_id": group_id,
                "error": error_msg
            })
    
    # 构建响应
    response = BroadcastResponse(
        success=success_count > 0,
        message=f"广播完成: 成功 {success_count}/{len(target_groups)} 个群组",
        total=len(target_groups),
        success_count=success_count,
        failed_count=failed_count,
        failed_groups=failed_groups
    )
    
    if invalid_groups:
        response.message += f"，{len(invalid_groups)} 个群组ID无效"
    
    logger.info(f"API广播完成: {response.message}")
    
    return response


@router.get("/groups", response_model=List[dict])
async def list_groups(_: bool = Depends(verify_api_key)):
    """
    获取所有已绑定的群组列表
    
    返回所有已绑定商户的群组信息
    """
    merchant_service = MerchantService()
    merchants = await merchant_service.get_all_active_merchants()
    
    # 过滤出群组（telegram_id < 0）
    groups = [
        {
            "group_id": m.telegram_id,
            "group_name": m.merchant_name,
            "merchant_code": m.merchant_code,
            "is_active": m.is_active
        }
        for m in merchants if m.telegram_id < 0
    ]
    
    logger.info(f"API查询群组列表: 共 {len(groups)} 个群组")
    
    return groups


@router.get("/health")
async def health_check():
    """健康检查接口（无需认证）"""
    return {
        "status": "ok",
        "service": "telegram-bot-api",
        "version": "1.0.0"
    }
