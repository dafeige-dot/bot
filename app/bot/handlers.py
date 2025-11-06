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
    
    # 检查是否在等待订单号（/orders 命令后）
    if context.user_data.get("awaiting_order_id"):
        await handle_order_search(update, context, text)
        return
    
    # 检查是否在等待订单号（旧逻辑）
    if context.user_data.get("awaiting_order_no"):
        await handle_order_search(update, context, text)
        return
    
    # 检查是否在等待广播消息
    if context.user_data.get("awaiting_broadcast"):
        await handle_broadcast_message(update, context, text)
        return
    
    # 默认回复
    await update.message.reply_text(
        "我不太明白您的意思。\n"
        "请使用 /help 查看可用命令。"
    )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理图片消息"""
    user = update.effective_user
    chat = update.effective_chat
    
    logger.info(f"收到用户 {user.id} 的图片")
    
    # 获取商户信息（使用聊天ID）
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(chat.id)
    
    if not merchant:
        await update.message.reply_text("❌ 您还未注册，请先使用 /start 命令注册")
        return
    
    # 获取用户语言
    lang = merchant.language if merchant else 'zh'
    
    # 检查OCR功能是否启用
    if not settings.ENABLE_OCR:
        if lang == 'en':
            await update.message.reply_text("❌ Image recognition is temporarily unavailable")
        else:
            await update.message.reply_text("❌ 图片识别功能暂时不可用")
        return
    
    # 🆕 检查图片是否带有文字说明（caption）
    caption_text = update.message.caption if update.message.caption else None
    
    if caption_text:
        # 用户发送了图片+文字，先尝试用文字作为订单号查询
        logger.info(f"图片附带文字: {caption_text}")
        
        # 调用后端 API 查询订单
        from app.utils.api_client import api_client
        result = await api_client.query_order(merchant.merchant_code, caption_text.strip())
        
        if result.get("code") == 200:
            # 找到订单，直接返回
            order_type = result.get("type", "")
            status = result.get("status", 0)
            status_desc = result.get("status_desc", "")
            order_price = result.get("order_price", "0")
            real_pay = result.get("real_pay", "0")
            platform_order_no = result.get("order_num", "")
            mch_order_no = result.get("mch_order_no", "")
            
            status_emoji = {
                0: '⏳',
                1: '🔄',
                2: '✅',
                3: '❌',
            }.get(status, '❓')
            
            if lang == 'en':
                type_text = "Payin Order" if order_type == "payin" else "Payout Order"
                result_text = (
                    f"✅ Order found!\n\n"
                    f"{status_emoji} {type_text}\n"
                    f"📝 Order No: {mch_order_no}\n"
                    f"💰 Amount: ₹{order_price}\n"
                    f"💳 Real Pay: ₹{real_pay}\n"
                    f"📊 Status: {status_desc}\n\n"
                    f"💡 Searched by caption: {caption_text}"
                )
            else:
                type_text = "代收订单" if order_type == "payin" else "代付订单"
                result_text = (
                    f"✅ 找到订单！\n\n"
                    f"{status_emoji} {type_text}\n"
                    f"📝 订单号：{mch_order_no}\n"
                    f"💰 订单金额：₹{order_price}\n"
                    f"💳 实际支付：₹{real_pay}\n"
                    f"📊 状态：{status_desc}\n\n"
                    f"💡 通过图片说明查询: {caption_text}"
                )
            
            await update.message.reply_text(result_text)
            logger.info(f"通过图片说明找到订单: {caption_text}")
            return
        else:
            # 文字查询未找到，提示将进行图片识别
            if lang == 'en':
                hint_msg = (
                    f"💡 Order not found by caption '{caption_text}'\n"
                    f"🔄 Will try to recognize the image..."
                )
            else:
                hint_msg = (
                    f"💡 图片说明 '{caption_text}' 未找到订单\n"
                    f"🔄 将尝试识别图片..."
                )
            await update.message.reply_text(hint_msg)
    
    # 获取最大的图片
    photo = update.message.photo[-1]
    
    # 验证图片大小
    if not validate_image_size(photo.file_size, settings.MAX_IMAGE_SIZE_MB):
        if lang == 'en':
            await update.message.reply_text(
                f"❌ Image too large\n\n"
                f"Maximum size: {settings.MAX_IMAGE_SIZE_MB}MB"
            )
        else:
            await update.message.reply_text(
                f"❌ 图片太大\n\n"
                f"图片大小不能超过 {settings.MAX_IMAGE_SIZE_MB}MB"
            )
        return
    
    # 发送处理中消息
    if lang == 'en':
        processing_msg = await update.message.reply_text("🔄 Processing image, please wait...")
    else:
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
            if lang == 'en':
                await processing_msg.edit_text(
                    f"❌ Recognition failed\n\n"
                    f"Reason: {ocr_result['error']}\n\n"
                    f"Please try:\n"
                    f"• Upload clearer image\n"
                    f"• Ensure order number is fully visible\n"
                    f"• Or send image with order number as caption"
                )
            else:
                await processing_msg.edit_text(
                    f"❌ 识别失败\n\n"
                    f"原因：{ocr_result['error']}\n\n"
                    f"请尝试：\n"
                    f"• 上传更清晰的图片\n"
                    f"• 确保订单号完整可见\n"
                    f"• 或发送图片时附带订单号文字"
                )
            return
        
        # 尝试提取支付信息（金额、UTR、UPI）
        from app.utils.payment_ocr import parse_payment_screenshot
        payment_info = parse_payment_screenshot(ocr_result.get('text', ''))
        
        # 如果识别到 UPI，优先处理 UPI 查询
        if payment_info.get('upi'):
            await handle_upi_check(
                update, context, processing_msg, 
                merchant, payment_info, lang
            )
            return
        
        # 提取订单号
        order_nos = ocr_result.get('order_numbers', [])
        
        if not order_nos:
            # 如果没有订单号，但有支付信息，显示支付信息
            if payment_info.get('amount') or payment_info.get('utr'):
                payment_text = "🧾 识别到支付信息：\n\n"
                if payment_info.get('amount'):
                    payment_text += f"💰 金额: ₹{payment_info['amount']}\n"
                if payment_info.get('utr'):
                    payment_text += f"🔢 UTR: {payment_info['utr']}\n"
                if payment_info.get('sender'):
                    payment_text += f"👤 付款人: {payment_info['sender']}\n"
                if payment_info.get('bank'):
                    payment_text += f"🏦 银行: {payment_info['bank']}\n"
                
                payment_text += "\n⚠️ 未找到 UPI 地址\n"
                payment_text += "💡 如需查询订单，请发送订单号"
                
                await processing_msg.edit_text(payment_text)
                return
            
            if lang == 'en':
                await processing_msg.edit_text(
                    "❓ No order number found\n\n"
                    "Recognized text:\n"
                    f"{ocr_result.get('text', 'None')[:200]}\n\n"
                    "💡 Tip: Send image with order number as caption\n"
                    "Example: [Image] ORD123456"
                )
            else:
                await processing_msg.edit_text(
                    "❓ 未识别到订单号\n\n"
                    "识别到的文本：\n"
                    f"{ocr_result.get('text', '无')[:200]}\n\n"
                    "💡 提示：可以发送图片时附带订单号文字\n"
                    "例如：[图片] ORD123456"
                )
            return
        
        # 查询订单 - 调用后端 API
        from app.utils.api_client import api_client
        found_results = []
        
        for order_no in order_nos:
            result = await api_client.query_order(merchant.merchant_code, order_no.strip())
            if result.get("code") == 200:
                found_results.append(result)
        
        if not found_results:
            if lang == 'en':
                await processing_msg.edit_text(
                    f"❓ Order not found\n\n"
                    f"Recognized order numbers:\n"
                    f"{', '.join(order_nos)}\n\n"
                    f"Possible reasons:\n"
                    f"• Order number recognition error\n"
                    f"• Order not in your account\n"
                    f"• Order not in system\n\n"
                    f"💡 Tip: Send image with order number as caption"
                )
            else:
                await processing_msg.edit_text(
                    f"❓ 未找到订单\n\n"
                    f"识别到的订单号：\n"
                    f"{', '.join(order_nos)}\n\n"
                    f"可能的原因：\n"
                    f"• 订单号识别错误\n"
                    f"• 订单不属于您的账户\n"
                    f"• 订单尚未录入系统\n\n"
                    f"💡 提示：可发送图片时附带订单号文字"
                )
            return
        
        # 显示找到的订单
        if lang == 'en':
            result_text = f"✅ Success! Found {len(found_results)} order(s):\n\n"
        else:
            result_text = f"✅ 识别成功！找到 {len(found_results)} 个订单：\n\n"
        
        for order_result in found_results:
            order_type = order_result.get("type", "")
            status = order_result.get("status", 0)
            status_desc = order_result.get("status_desc", "")
            order_price = order_result.get("order_price", "0")
            real_pay = order_result.get("real_pay", "0")
            mch_order_no = order_result.get("mch_order_no", "")
            
            status_emoji = {
                0: '⏳',
                1: '🔄',
                2: '✅',
                3: '❌',
            }.get(status, '❓')
            
            if lang == 'en':
                type_text = "Payin" if order_type == "payin" else "Payout"
                result_text += (
                    f"{status_emoji} [{type_text}] {mch_order_no}\n"
                    f"💰 Amount: ₹{order_price}\n"
                    f"💳 Real Pay: ₹{real_pay}\n"
                    f"📊 Status: {status_desc}\n\n"
                )
            else:
                type_text = "代收" if order_type == "payin" else "代付"
                result_text += (
                    f"{status_emoji} [{type_text}] {mch_order_no}\n"
                    f"💰 订单金额：₹{order_price}\n"
                    f"💳 实际支付：₹{real_pay}\n"
                    f"📊 状态：{status_desc}\n\n"
                )
        
        await processing_msg.edit_text(result_text)
        
        logger.info(f"OCR识别成功，找到 {len(found_results)} 个订单")
        
    except Exception as e:
        logger.exception(f"处理图片时出错: {e}")
        if lang == 'en':
            await processing_msg.edit_text(
                f"❌ Processing failed\n\n"
                f"An error occurred, please try again later."
            )
        else:
            await processing_msg.edit_text(
                f"❌ 处理失败\n\n"
                f"发生了一些错误，请稍后重试。"
            )


async def handle_upi_check(update: Update, context: ContextTypes.DEFAULT_TYPE,
                          processing_msg, merchant, payment_info: dict, lang: str):
    """处理 UPI 查询"""
    from app.utils.api_client import api_client
    
    upi = payment_info.get('upi')
    utr = payment_info.get('utr')
    amount = payment_info.get('amount')
    
    logger.info(f"开始 UPI 查询: UPI={upi}, UTR={utr}, Amount={amount}")
    
    try:
        # 调用后端 API 查询 UPI
        result = await api_client.check_upi(merchant.merchant_code, upi)
        
        # 构建显示信息
        payment_text = "🧾 识别到支付信息：\n\n"
        if amount:
            payment_text += f"💰 金额: ₹{amount}\n"
        if utr:
            payment_text += f"🔢 UTR: {utr}\n"
        payment_text += f"📱 UPI: {upi}\n"
        if payment_info.get('sender'):
            payment_text += f"👤 付款人: {payment_info['sender']}\n"
        if payment_info.get('bank'):
            payment_text += f"🏦 银行: {payment_info['bank']}\n"
        
        payment_text += "\n" + "="*30 + "\n\n"
        
        # 处理 UPI 查询结果
        if result.get("code") == 200:
            is_upi = result.get("is_upi", 0)
            
            if is_upi == 1:
                # UPI 是我们的
                payment_text += "✅ 这是我们的 UPI 地址\n\n"
                if utr:
                    payment_text += (
                        f"⚠️ 但是 UTR {utr} 可能:\n"
                        f"• UTR 不正确\n"
                        f"• 或已被其他商户领取\n\n"
                        f"📞 请联系客服确认\n"
                    )
                else:
                    payment_text += "💡 请提供 UTR 以便进一步核实"
            else:
                # UPI 不是我们的
                payment_text += (
                    f"❌ 这不是我们的 UPI 地址\n\n"
                    f"⚠️ 请确认:\n"
                    f"• UPI 地址是否正确\n"
                    f"• 是否转错账户\n\n"
                    f"📞 如有疑问请联系客服"
                )
        else:
            # 查询失败
            error_msg = result.get("msg", "Unknown error")
            payment_text += f"❌ UPI 查询失败\n\n错误: {error_msg}"
        
        await processing_msg.edit_text(payment_text)
        logger.info(f"UPI 查询完成: is_upi={result.get('is_upi', 'N/A')}")
        
    except Exception as e:
        logger.exception(f"UPI 查询异常: {e}")
        await processing_msg.edit_text(
            "❌ UPI 查询失败\n\n"
            "系统错误，请稍后重试"
        )


async def handle_order_search(update: Update, context: ContextTypes.DEFAULT_TYPE, order_no: str):
    """处理订单搜索 - 调用后端 API"""
    user = update.effective_user
    chat = update.effective_chat
    from app.i18n import get_language
    
    try:
        merchant_service = MerchantService()
        merchant = await merchant_service.get_by_telegram_id(chat.id)
        
        if not merchant:
            await update.message.reply_text("❌ 请先注册")
            return
        
        lang = get_language(user.id)
        
        # 发送查询中提示
        if lang == "en":
            status_msg = await update.message.reply_text(f"🔍 Querying order {order_no}...")
        else:
            status_msg = await update.message.reply_text(f"🔍 正在查询订单 {order_no}...")
        
        try:
            # 调用后端 API 查询订单
            from app.utils.api_client import api_client
            result = await api_client.query_order(merchant.merchant_code, order_no.strip())
            
            # 删除状态消息
            try:
                await status_msg.delete()
            except Exception:
                pass  # 忽略删除消息失败
        except Exception as api_error:
            logger.exception(f"订单查询 API 调用失败: {api_error}")
            
            try:
                await status_msg.delete()
            except Exception:
                pass
            
            if lang == "en":
                await update.message.reply_text(
                    "❌ Query failed\n\n"
                    "System error occurred\n"
                    "Please try again later"
                )
            else:
                await update.message.reply_text(
                    "❌ 查询失败\n\n"
                    "系统发生错误\n"
                    "请稍后重试"
                )
            
            context.user_data.pop("awaiting_order_no", None)
            context.user_data.pop("awaiting_order_id", None)
            return
    
        # 处理响应
        if result.get("code") == 200:
            order_type = result.get("type", "")
            status = result.get("status", 0)
            status_desc = result.get("status_desc", "")
            order_price = result.get("order_price", "0")
            real_pay = result.get("real_pay", "0")
            platform_order_no = result.get("order_num", "")
            mch_order_no = result.get("mch_order_no", "")
            
            # 状态 emoji
            status_emoji = {
                0: '⏳',
                1: '🔄',
                2: '✅',
                3: '❌',
            }.get(status, '❓')
            
            if lang == "en":
                type_text = "Payin Order" if order_type == "payin" else "Payout Order"
                order_text = (
                    f"{status_emoji} {type_text}\n\n"
                    f"📝 Order No: {mch_order_no}\n"
                    f"🔢 Platform Order No: {platform_order_no}\n"
                    f"💰 Order Amount: ₹{order_price}\n"
                    f"💳 Real Pay: ₹{real_pay}\n"
                    f"📊 Status: {status_desc}\n"
                )
            else:
                type_text = "代收订单" if order_type == "payin" else "代付订单"
                order_text = (
                    f"{status_emoji} {type_text}\n\n"
                    f"📝 订单号：{mch_order_no}\n"
                    f"🔢 平台订单号：{platform_order_no}\n"
                    f"💰 订单金额：₹{order_price}\n"
                    f"💳 实际支付：₹{real_pay}\n"
                    f"📊 状态：{status_desc}\n"
                )
            
            # 如果是失败状态且有错误消息
            if status == 3 and result.get("msg"):
                if lang == "en":
                    order_text += f"\n❌ Reason: {result.get('msg')}"
                else:
                    order_text += f"\n❌ 失败原因：{result.get('msg')}"
            
            await update.message.reply_text(order_text)
        else:
            error_msg = result.get("msg", "Unknown error")
            if lang == "en":
                await update.message.reply_text(
                    f"❌ Order not found\n\n"
                    f"Order No: {order_no}\n"
                    f"Reason: {error_msg}\n\n"
                    f"Please check the order number."
                )
            else:
                await update.message.reply_text(
                    f"❌ 未找到订单\n\n"
                    f"订单号：{order_no}\n"
                    f"原因：{error_msg}\n\n"
                    f"请检查订单号是否正确。"
                )
        
        # 清除等待状态
        context.user_data.pop("awaiting_order_no", None)
        context.user_data.pop("awaiting_order_id", None)
        
    except Exception as e:
        logger.exception(f"处理订单搜索时发生错误: {e}")
        
        # 确保机器人不会崩溃
        try:
            lang = get_language(user.id)
            if lang == "en":
                await update.message.reply_text(
                    "❌ An error occurred\n\n"
                    "Please try again later"
                )
            else:
                await update.message.reply_text(
                    "❌ 发生错误\n\n"
                    "请稍后重试"
                )
        except Exception:
            pass
        
        # 清除等待状态
        try:
            context.user_data.pop("awaiting_order_no", None)
            context.user_data.pop("awaiting_order_id", None)
        except Exception:
            pass


async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """处理广播消息"""
    from app.config import settings
    from app.services.merchant import MerchantService
    
    user = update.effective_user
    
    # 再次检查权限
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此功能")
        context.user_data.pop("awaiting_broadcast", None)
        return
    
    # 确认发送
    if not context.user_data.get("broadcast_confirmed"):
        context.user_data["broadcast_message"] = text
        context.user_data["broadcast_confirmed"] = True
        
        # 获取商户数量
        merchant_service = MerchantService()
        merchants = await merchant_service.get_all_active_merchants()
        
        await update.message.reply_text(
            f"📢 广播消息预览：\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{text}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 将发送给 {len(merchants)} 个商户\n\n"
            f"确认发送吗？\n"
            f"• 回复 '确认' 开始发送\n"
            f"• 回复 '取消' 或 /cancel 取消"
        )
        return
    
    # 检查确认
    if text.lower() not in ['确认', 'yes', 'y', '是']:
        context.user_data.clear()
        await update.message.reply_text("❌ 广播已取消")
        return
    
    # 执行广播
    broadcast_message = context.user_data.get("broadcast_message", "")
    context.user_data.clear()
    
    processing_msg = await update.message.reply_text("⏳ 正在发送广播消息...")
    
    try:
        merchant_service = MerchantService()
        merchants = await merchant_service.get_all_active_merchants()
        
        success_count = 0
        failed_count = 0
        
        for merchant in merchants:
            try:
                await context.bot.send_message(
                    chat_id=merchant.telegram_id,
                    text=f"📢 系统广播\n\n{broadcast_message}"
                )
                success_count += 1
                
                # 延迟避免限流
                import asyncio
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"发送给商户 {merchant.id} 失败: {e}")
                failed_count += 1
        
        await processing_msg.edit_text(
            f"✅ 广播发送完成！\n\n"
            f"📊 发送统计：\n"
            f"✅ 成功：{success_count}\n"
            f"❌ 失败：{failed_count}\n"
            f"📈 成功率：{success_count/(success_count+failed_count)*100:.1f}%"
        )
        
    except Exception as e:
        logger.exception(f"广播发送失败: {e}")
        await processing_msg.edit_text(
            f"❌ 广播发送失败\n\n"
            f"错误信息：{str(e)}"
        )


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

