"""
消息处理器模块
"""
import os
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from app.config import settings
from app.services.merchant import MerchantService
from app.services.ocr import OCRService
from app.services.order import OrderService
from app.utils.helpers import validate_image_size


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文本消息"""
    user = update.effective_user
    text = update.message.text
    
    logger.info(f"收到用户 {user.id} 的文本消息: {text[:50]}")
    
    # 检查是否在等待商户验证码
    if context.user_data.get("awaiting_merchant_code"):
        await handle_merchant_code(update, context, text)
        return
    
    # 检查是否在等待订单号
    if context.user_data.get("awaiting_order_no"):
        await handle_order_search(update, context, text)
        return
    
    # 默认回复
    await update.message.reply_text(
        "我不太明白您的意思。\n"
        "请使用 /help 查看可用命令。"
    )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理图片消息"""
    user = update.effective_user
    
    logger.info(f"收到用户 {user.id} 的图片")
    
    # 获取商户信息
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    if not merchant:
        await update.message.reply_text("❌ 您还未注册，请先使用 /start 命令注册")
        return
    
    # 检查OCR功能是否启用
    if not settings.ENABLE_OCR:
        await update.message.reply_text("❌ 图片识别功能暂时不可用")
        return
    
    # 获取最大的图片
    photo = update.message.photo[-1]
    
    # 验证图片大小
    if not validate_image_size(photo.file_size, settings.MAX_IMAGE_SIZE_MB):
        await update.message.reply_text(
            f"❌ 图片太大\n\n"
            f"图片大小不能超过 {settings.MAX_IMAGE_SIZE_MB}MB"
        )
        return
    
    # 发送处理中消息
    processing_msg = await update.message.reply_text("🔄 正在处理图片，请稍候...")
    
    try:
        # 下载图片
        file = await context.bot.get_file(photo.file_id)
        
        # 保存路径
        file_ext = Path(file.file_path).suffix or ".jpg"
        file_name = f"{user.id}_{photo.file_id}{file_ext}"
        file_path = Path(settings.TEMP_DIR) / file_name
        
        await file.download_to_drive(file_path)
        
        logger.info(f"图片已下载: {file_path}")
        
        # 进行OCR识别
        ocr_service = OCRService()
        ocr_result = await ocr_service.recognize_order_image(str(file_path))
        
        # 删除临时文件
        if file_path.exists():
            os.remove(file_path)
        
        if not ocr_result['success']:
            await processing_msg.edit_text(
                f"❌ 识别失败\n\n"
                f"原因：{ocr_result['error']}\n\n"
                f"请尝试：\n"
                f"• 上传更清晰的图片\n"
                f"• 确保订单号完整可见"
            )
            return
        
        # 提取订单号
        order_nos = ocr_result.get('order_numbers', [])
        
        if not order_nos:
            await processing_msg.edit_text(
                "❓ 未识别到订单号\n\n"
                "识别到的文本：\n"
                f"{ocr_result.get('text', '无')[:200]}\n\n"
                "请手动输入订单号或上传更清晰的图片。"
            )
            return
        
        # 查询订单
        order_service = OrderService()
        found_orders = []
        
        for order_no in order_nos:
            order = await order_service.get_by_order_no(order_no)
            if order:
                found_orders.append(order)
        
        if not found_orders:
            await processing_msg.edit_text(
                f"❓ 未找到订单\n\n"
                f"识别到的订单号：\n"
                f"{', '.join(order_nos)}\n\n"
                f"可能的原因：\n"
                f"• 订单号识别错误\n"
                f"• 订单不属于您的账户\n"
                f"• 订单尚未录入系统"
            )
            return
        
        # 显示找到的订单
        result_text = f"✅ 识别成功！找到 {len(found_orders)} 个订单：\n\n"
        
        for order in found_orders:
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅',
                'cancelled': '❌',
            }.get(order.order_status, '❓')
            
            result_text += (
                f"{status_emoji} 订单号：{order.order_no}\n"
                f"金额：¥{order.amount:,.2f}\n"
                f"状态：{order.order_status}\n"
                f"时间：{order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            )
        
        await processing_msg.edit_text(result_text)
        
        logger.info(f"OCR识别成功，找到 {len(found_orders)} 个订单")
        
    except Exception as e:
        logger.exception(f"处理图片时出错: {e}")
        await processing_msg.edit_text(
            f"❌ 处理失败\n\n"
            f"发生了一些错误，请稍后重试。"
        )


async def handle_merchant_code(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str):
    """处理商户验证码"""
    user = update.effective_user
    
    # TODO: 验证商户验证码
    # 这里简化处理，实际应该验证验证码的有效性
    
    merchant_service = MerchantService()
    
    try:
        # 创建商户
        merchant = await merchant_service.create_merchant(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            merchant_code=code,
        )
        
        context.user_data.pop("awaiting_merchant_code", None)
        
        await update.message.reply_text(
            f"✅ 注册成功！\n\n"
            f"欢迎您，{merchant.full_name}！\n"
            f"商户编号：{merchant.merchant_code}\n\n"
            f"请使用 /help 查看可用功能。"
        )
        
    except Exception as e:
        logger.error(f"创建商户失败: {e}")
        await update.message.reply_text(
            f"❌ 注册失败\n\n"
            f"验证码可能无效或已被使用。\n"
            f"请联系管理员获取新的验证码。"
        )


async def handle_order_search(update: Update, context: ContextTypes.DEFAULT_TYPE, order_no: str):
    """处理订单搜索"""
    user = update.effective_user
    
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    if not merchant:
        await update.message.reply_text("❌ 请先注册")
        return
    
    # 查询订单
    order_service = OrderService()
    order = await order_service.get_by_order_no(order_no)
    
    if not order or order.merchant_id != merchant.id:
        await update.message.reply_text(
            f"❌ 未找到订单\n\n"
            f"订单号：{order_no}\n\n"
            f"请检查订单号是否正确。"
        )
        return
    
    # 显示订单详情
    status_emoji = {
        'pending': '⏳',
        'processing': '🔄',
        'completed': '✅',
        'cancelled': '❌',
    }.get(order.order_status, '❓')
    
    order_text = (
        f"{status_emoji} 订单详情\n\n"
        f"订单号：{order.order_no}\n"
        f"金额：¥{order.amount:,.2f}\n"
        f"状态：{order.order_status}\n"
        f"支付状态：{order.payment_status}\n"
        f"创建时间：{order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
    )
    
    if order.product_name:
        order_text += f"商品：{order.product_name}\n"
    
    if order.customer_name:
        order_text += f"客户：{order.customer_name}\n"
    
    await update.message.reply_text(order_text)
    
    context.user_data.pop("awaiting_order_no", None)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """错误处理器"""
    logger.error(f"更新 {update} 导致错误: {context.error}", exc_info=context.error)
    
    # 如果有update对象，尝试通知用户
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ 抱歉，处理您的请求时发生了错误。\n"
                "我们已记录此问题，请稍后重试。"
            )
        except Exception as e:
            logger.error(f"发送错误消息失败: {e}")

