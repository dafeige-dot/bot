"""
消息处理器模块
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from app.config import settings
from app.services.merchant import MerchantService


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
    
    # 检查是否在等待频道广播消息
    if context.user_data.get("awaiting_broadcast_channel"):
        await handle_broadcast_channel_message(update, context, text)
        return
    
    # 检查是否在等待定向群组广播消息
    if context.user_data.get("awaiting_dxgb_message"):
        await handle_dxgb_message(update, context, text)
        return
    
    # 普通文本消息不再回复（仅处理命令与图片）
    return


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理图片消息"""
    user = update.effective_user
    chat = update.effective_chat
    
    logger.info(f"收到用户 {user.id} 的图片")
    
    # 检查是否在等待广播消息（优先处理）
    if context.user_data.get("awaiting_broadcast"):
        await handle_broadcast_photo(update, context)
        return
    
    # 检查是否在等待频道广播消息
    if context.user_data.get("awaiting_broadcast_channel"):
        await handle_broadcast_channel_photo(update, context)
        return
    
    # 检查是否在等待定向群组广播图片
    if context.user_data.get("awaiting_dxgb_message"):
        await handle_dxgb_photo(update, context)
        return
    
    # 优化后的逻辑：
    # 1. 如果只有图片没有标题(caption)，不做处理
    # 2. 如果包含标题，则根据标题进行查询订单
    
    caption_text = update.message.caption
    
    if not caption_text:
        # 没有标题，不做处理
        logger.info(f"图片无标题，忽略处理 (Chat ID: {chat.id})")
        return
    
    # 有标题，根据标题查询订单
    logger.info(f"图片附带标题: {caption_text}，将进行订单查询")
    # 获取最大尺寸的图片对象，传给 handle_order_search 以便查询成功后另存
    photo_obj = update.message.photo[-1] if update.message.photo else None
    await handle_order_search(update, context, caption_text.strip(), photo_obj=photo_obj)


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
        if lang == 'en':
            payment_text = "🧾 Detected payment info:\n\n"
            if amount:
                payment_text += f"💰 Amount: ₹{amount}\n"
            if utr:
                payment_text += f"🔢 UTR: {utr}\n"
            payment_text += f"📱 UPI: {upi}\n"
            if payment_info.get('sender'):
                payment_text += f"👤 Payer: {payment_info['sender']}\n"
            if payment_info.get('bank'):
                payment_text += f"🏦 Bank: {payment_info['bank']}\n"
        else:
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
        
        # 处理 UPI 查询结果（容错，兼容 code 为字符串，且 is_upi 位于 data 中）
        ok = isinstance(result, dict) and str(result.get("code")) == "200"
        data_section = result.get("data") if isinstance(result.get("data"), dict) else {}
        raw_is_upi = data_section.get("is_upi", result.get("is_upi"))
        is_upi = None
        try:
            if raw_is_upi is not None:
                is_upi = 1 if int(raw_is_upi) == 1 else 0
        except Exception:
            is_upi = None

        if ok and is_upi is not None:
            if is_upi == 1:
                if lang == 'en':
                    payment_text += "✅ This is our UPI address\n\n"
                    if utr:
                        payment_text += (
                            f"⚠️ However, UTR {utr} may:\n"
                            f"• Be incorrect\n"
                            f"• Or already be claimed by another merchant\n\n"
                            f"📞 Please contact support to confirm\n"
                        )
                    else:
                        payment_text += "💡 Please provide UTR for further verification"
                else:
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
                if lang == 'en':
                    payment_text += (
                        f"❌ This is not our UPI address\n\n"
                        f"⚠️ Please check:\n"
                        f"• Whether the UPI address is correct\n"
                        f"• Whether funds were transferred to the wrong account\n\n"
                        f"📞 Contact support if needed"
                    )
                else:
                    payment_text += (
                        f"❌ 这不是我们的 UPI 地址\n\n"
                        f"⚠️ 请确认:\n"
                        f"• UPI 地址是否正确\n"
                        f"• 是否转错账户\n\n"
                        f"📞 如有疑问请联系客服"
                    )
        else:
            payment_text += ("Not received yet" if lang == 'en' else "暂未收到")
        
        await processing_msg.edit_text(payment_text)
        logger.info(f"UPI 查询完成: is_upi={is_upi if is_upi is not None else 'N/A'}")
        
    except Exception:
        await processing_msg.edit_text("Not received yet" if lang == 'en' else "暂未收到")


async def handle_order_search(update: Update, context: ContextTypes.DEFAULT_TYPE, order_no: str, photo_obj=None):
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
            
            # 如果有图片且获取到平台订单号，将图片另存到 trans/日期 目录
            if photo_obj and platform_order_no:
                try:
                    import os
                    import pathlib
                    from datetime import datetime
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    trans_dir = pathlib.Path("trans") / date_str
                    trans_dir.mkdir(parents=True, exist_ok=True)
                    # 下载图片文件
                    tg_file = await context.bot.get_file(photo_obj.file_id)
                    file_path = tg_file.file_path or ""
                    # 从文件路径推断扩展名，默认 .jpg
                    ext = os.path.splitext(file_path)[1] if file_path else ".jpg"
                    if not ext:
                        ext = ".jpg"
                    save_path = trans_dir / f"{platform_order_no}{ext}"
                    await tg_file.download_to_drive(str(save_path))
                    logger.info(f"图片已另存: {save_path}")
                except Exception as save_err:
                    logger.warning(f"图片另存失败: {save_err}")
            mch_order_no = result.get("mch_order_no", "")
            utr = result.get("utr", "")
            
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
                    f"📊 Utr: {utr}\n"
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
                    f"📊 Utr：{utr}\n"
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
    broadcast_photo_file_id = context.user_data.get("broadcast_photo_file_id")
    broadcast_caption = context.user_data.get("broadcast_caption", "")
    context.user_data.clear()
    
    processing_msg = await update.message.reply_text("⏳ 正在发送广播消息...")
    
    try:
        merchant_service = MerchantService()
        merchants = await merchant_service.get_all_active_merchants()
        
        success_count = 0
        failed_count = 0
        
        for merchant in merchants:
            try:
                # 如果有图片，发送图片+说明
                if broadcast_photo_file_id:
                    caption_text = f"📢 系统广播\n\n{broadcast_caption}" if broadcast_caption else "📢 系统广播"
                    await context.bot.send_photo(
                        chat_id=merchant.telegram_id,
                        photo=broadcast_photo_file_id,
                        caption=caption_text
                    )
                else:
                    # 否则发送纯文本消息
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


async def handle_broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理广播图片消息"""
    from app.config import settings
    from app.services.merchant import MerchantService
    
    user = update.effective_user
    
    # 再次检查权限
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此功能")
        context.user_data.pop("awaiting_broadcast", None)
        return
    
    # 获取图片和说明文字
    photo = update.message.photo[-1]  # 获取最大的图片
    caption = update.message.caption if update.message.caption else ""
    
    # 确认发送
    if not context.user_data.get("broadcast_confirmed"):
        # 保存图片信息
        context.user_data["broadcast_photo_file_id"] = photo.file_id
        context.user_data["broadcast_caption"] = caption
        context.user_data["broadcast_confirmed"] = True
        
        # 获取商户数量
        merchant_service = MerchantService()
        merchants = await merchant_service.get_all_active_merchants()
        
        # 显示预览（转发图片）
        preview_text = (
            f"📢 广播图片消息预览：\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📸 图片 + 说明文字\n"
        )
        if caption:
            preview_text += f"💬 说明：{caption}\n"
        preview_text += (
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 将发送给 {len(merchants)} 个商户\n\n"
            f"确认发送吗？\n"
            f"• 回复 '确认' 开始发送\n"
            f"• 回复 '取消' 或 /cancel 取消"
        )
        
        await update.message.reply_text(preview_text)
        return
    
    # 如果已确认，检查是否是确认消息（这种情况不应该发生，因为这是photo_handler）
    # 正常流程是：发图片 -> 预览 -> 发文字"确认" -> handle_broadcast_message处理
    # 所以这里只处理第一次发送图片的情况
    await update.message.reply_text(
        "⚠️ 请回复文字 '确认' 来发送广播，或回复 '取消' 来取消"
    )


async def handle_broadcast_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """处理频道广播文本消息"""
    from app.config import settings
    
    user = update.effective_user
    
    # 再次检查权限
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此功能")
        context.user_data.pop("awaiting_broadcast_channel", None)
        return
    
    channel_id = context.user_data.get("broadcast_channel_id")
    channel_title = context.user_data.get("broadcast_channel_title", "未知频道")
    
    if not channel_id:
        await update.message.reply_text("❌ 频道信息丢失，请重新使用 /broadcast_channel 命令")
        context.user_data.clear()
        return
    
    # 确认发送
    if not context.user_data.get("broadcast_channel_confirmed"):
        context.user_data["broadcast_channel_message"] = text
        context.user_data["broadcast_channel_confirmed"] = True
        
        await update.message.reply_text(
            f"📢 频道广播消息预览：\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{text}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📢 目标频道：{channel_title}\n"
            f"🆔 频道ID：{channel_id}\n\n"
            f"确认发送吗？\n"
            f"• 回复 '确认' 开始发送\n"
            f"• 回复 '取消' 或 /cancel 取消"
        )
        return
    
    # 检查确认
    if text.lower() not in ['确认', 'yes', 'y', '是']:
        context.user_data.clear()
        await update.message.reply_text("❌ 频道广播已取消")
        return
    
    # 执行频道广播
    broadcast_message = context.user_data.get("broadcast_channel_message", "")
    broadcast_photo_file_id = context.user_data.get("broadcast_channel_photo_file_id")
    broadcast_caption = context.user_data.get("broadcast_channel_caption", "")
    context.user_data.clear()
    
    processing_msg = await update.message.reply_text("⏳ 正在发送到频道...")
    
    try:
        # 如果有图片，发送图片+说明
        if broadcast_photo_file_id:
            await context.bot.send_photo(
                chat_id=channel_id,
                photo=broadcast_photo_file_id,
                caption=broadcast_caption if broadcast_caption else None
            )
        else:
            # 否则发送纯文本消息
            await context.bot.send_message(
                chat_id=channel_id,
                text=broadcast_message
            )
        
        await processing_msg.edit_text(
            f"✅ 消息已成功发送到频道！\n\n"
            f"📢 频道：{channel_title}\n"
            f"🆔 ID：{channel_id}"
        )
        
    except Exception as e:
        logger.exception(f"频道广播发送失败: {e}")
        await processing_msg.edit_text(
            f"❌ 发送到频道失败\n\n"
            f"错误信息：{str(e)}\n\n"
            f"请检查：\n"
            f"• Bot是否仍是频道管理员\n"
            f"• Bot是否有发送消息权限"
        )


async def handle_broadcast_channel_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理频道广播图片消息"""
    from app.config import settings
    
    user = update.effective_user
    
    # 再次检查权限
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此功能")
        context.user_data.pop("awaiting_broadcast_channel", None)
        return
    
    channel_id = context.user_data.get("broadcast_channel_id")
    channel_title = context.user_data.get("broadcast_channel_title", "未知频道")
    
    if not channel_id:
        await update.message.reply_text("❌ 频道信息丢失，请重新使用 /broadcast_channel 命令")
        context.user_data.clear()
        return
    
    # 获取图片和说明文字
    photo = update.message.photo[-1]  # 获取最大的图片
    caption = update.message.caption if update.message.caption else ""
    
    # 确认发送
    if not context.user_data.get("broadcast_channel_confirmed"):
        # 保存图片信息
        context.user_data["broadcast_channel_photo_file_id"] = photo.file_id
        context.user_data["broadcast_channel_caption"] = caption
        context.user_data["broadcast_channel_confirmed"] = True
        
        # 显示预览
        preview_text = (
            f"📢 频道广播图片消息预览：\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📸 图片 + 说明文字\n"
        )
        if caption:
            preview_text += f"💬 说明：{caption}\n"
        preview_text += (
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📢 目标频道：{channel_title}\n"
            f"🆔 频道ID：{channel_id}\n\n"
            f"确认发送吗？\n"
            f"• 回复 '确认' 开始发送\n"
            f"• 回复 '取消' 或 /cancel 取消"
        )
        
        await update.message.reply_text(preview_text)
        return
    
    # 如果已确认，提示用户回复文字确认
    await update.message.reply_text(
        "⚠️ 请回复文字 '确认' 来发送到频道，或回复 '取消' 来取消"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """错误处理器"""
    import traceback
    from telegram.error import TimedOut, NetworkError, TelegramError
    
    error = context.error
    
    # 记录错误详情
    if isinstance(error, TimedOut):
        logger.warning(f"Telegram API 超时: {update}")
    elif isinstance(error, NetworkError):
        logger.error(f"网络错误: {error}", exc_info=error)
    else:
        logger.error(f"更新 {update} 导致错误: {error}", exc_info=error)
    
    # 如果有update对象，尝试通知用户（但不要因为通知失败而崩溃）
    if isinstance(update, Update) and update.effective_message:
        try:
            # 获取用户语言
            lang = 'zh'
            if update.effective_user:
                lang_code = getattr(update.effective_user, 'language_code', '')
                if lang_code and lang_code.startswith('en'):
                    lang = 'en'
            
            if lang == 'en':
                error_msg = (
                    "❌ Sorry, an error occurred while processing your request.\n"
                    "The issue has been logged. Please try again later."
                )
            else:
                error_msg = (
                    "❌ 抱歉，处理您的请求时发生了错误。\n"
                    "我们已记录此问题，请稍后重试。"
                )
            
            # 使用asyncio超时保护
            import asyncio
            await asyncio.wait_for(
                update.effective_message.reply_text(error_msg),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            logger.error("发送错误消息超时")
        except TelegramError as e:
            logger.error(f"发送错误消息失败 (TelegramError): {e}")
        except Exception as e:
            logger.error(f"发送错误消息失败: {e}")



async def handle_dxgb_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """处理定向群组广播文本消息"""
    from app.config import settings
    
    user = update.effective_user
    
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此功能")
        context.user_data.pop("awaiting_dxgb_message", None)
        return
    
    selected = context.user_data.get("dxgb_selected", [])
    merchants = context.user_data.get("dxgb_merchants", {})
    
    if not selected or not merchants:
        await update.message.reply_text("❌ 会话已过期，请重新使用 /dxgb 命令")
        context.user_data.clear()
        return
    
    # 确认发送
    if not context.user_data.get("dxgb_confirmed"):
        context.user_data["dxgb_message"] = text
        context.user_data["dxgb_confirmed"] = True
        
        selected_names = [merchants[tid] for tid in selected if tid in merchants]
        await update.message.reply_text(
            f"📢 定向群组广播预览：\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{text}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 目标群组 ({len(selected)}个)：\n"
            f"{'、'.join(selected_names[:5])}"
            f"{'...' if len(selected_names) > 5 else ''}\n\n"
            f"确认发送吗？\n"
            f"• 回复 '确认' 开始发送\n"
            f"• 回复 '取消' 或 /cancel 取消"
        )
        return
    
    # 检查确认
    if text.lower() not in ['确认', 'yes', 'y', '是']:
        context.user_data.clear()
        await update.message.reply_text("❌ 定向广播已取消")
        return
    
    # 执行广播
    broadcast_message = context.user_data.get("dxgb_message", "")
    broadcast_photo_file_id = context.user_data.get("dxgb_photo_file_id")
    broadcast_caption = context.user_data.get("dxgb_caption", "")
    
    context.user_data.clear()
    
    processing_msg = await update.message.reply_text(f"⏳ 正在发送到 {len(selected)} 个群组...")
    
    success_count = 0
    failed_count = 0
    failed_groups = []
    
    for group_id in selected:
        try:
            if broadcast_photo_file_id:
                await context.bot.send_photo(
                    chat_id=group_id,
                    photo=broadcast_photo_file_id,
                    caption=broadcast_caption if broadcast_caption else None
                )
            else:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=broadcast_message
                )
            success_count += 1
            
            # 延迟避免限流
            if settings.BROADCAST_DELAY_MS > 0:
                import asyncio
                await asyncio.sleep(settings.BROADCAST_DELAY_MS / 1000)
                
        except Exception as e:
            logger.error(f"发送到群组 {group_id} 失败: {e}")
            failed_count += 1
            group_name = merchants.get(group_id, str(group_id))
            failed_groups.append(f"{group_name}: {str(e)[:30]}")
    
    # 发送结果
    result_text = (
        f"✅ 定向广播完成\n\n"
        f"📊 发送统计：\n"
        f"• 成功：{success_count} 个群组\n"
        f"• 失败：{failed_count} 个群组\n"
    )
    
    if failed_groups:
        result_text += f"\n❌ 失败详情：\n" + "\n".join(failed_groups[:5])
        if len(failed_groups) > 5:
            result_text += f"\n... 等 {len(failed_groups)} 个"
    
    await processing_msg.edit_text(result_text)


async def handle_dxgb_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理定向群组广播图片消息"""
    from app.config import settings
    
    user = update.effective_user
    
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此功能")
        context.user_data.pop("awaiting_dxgb_message", None)
        return
    
    selected = context.user_data.get("dxgb_selected", [])
    merchants = context.user_data.get("dxgb_merchants", {})
    
    if not selected or not merchants:
        await update.message.reply_text("❌ 会话已过期，请重新使用 /dxgb 命令")
        context.user_data.clear()
        return
    
    # 获取图片
    photo = update.message.photo[-1]  # 最大尺寸
    caption = update.message.caption or ""
    
    # 确认发送
    if not context.user_data.get("dxgb_confirmed"):
        context.user_data["dxgb_photo_file_id"] = photo.file_id
        context.user_data["dxgb_caption"] = caption
        context.user_data["dxgb_confirmed"] = True
        
        selected_names = [merchants[tid] for tid in selected if tid in merchants]
        await update.message.reply_text(
            f"📢 定向群组广播图片预览：\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📸 图片" + (f" + 说明：{caption[:50]}..." if len(caption) > 50 else (f" + 说明：{caption}" if caption else "")) + "\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 目标群组 ({len(selected)}个)：\n"
            f"{'、'.join(selected_names[:5])}"
            f"{'...' if len(selected_names) > 5 else ''}\n\n"
            f"确认发送吗？\n"
            f"• 回复 '确认' 开始发送\n"
            f"• 回复 '取消' 或 /cancel 取消"
        )
        return
