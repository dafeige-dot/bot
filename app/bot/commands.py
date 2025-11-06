"""
命令处理模块
"""
from telegram import Update
from telegram.constants import ParseMode
from html import escape
from telegram.ext import ContextTypes
from loguru import logger

from app.bot.keyboards import (
    get_main_menu_keyboard,
    get_admin_menu_keyboard,
    get_broadcast_keyboard,
)
from app.services.merchant import MerchantService
from app.services.balance import BalanceService
from app.services.order import OrderService
from app.config import settings
from app.i18n import get_text, set_language, get_language


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user = update.effective_user
    logger.info(f"用户 {user.id} ({user.username}) 启动了机器人")
    
    # 检查当前聊天是否已绑定
    # 使用 chat.id 而不是 user.id，这样群聊和私聊都用聊天ID
    chat = update.effective_chat
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(chat.id)
    
    if not merchant:
        # 新用户，提示联系管理员
        chat = update.effective_chat
        
        if chat.type == 'private':
            # 私聊
            welcome_text = (
                f"👋 欢迎使用 / Welcome to {settings.APP_NAME}！\n\n"
                f"您好 / Hello，{user.first_name}！\n\n"
                f"🔐 您还未绑定商户账号\n"
                f"🔐 You haven't bound a merchant account yet\n\n"
                f"📞 请联系管理员在此私聊中执行绑定\n"
                f"📞 Please contact administrator to bind in this chat\n\n"
                f"💡 管理员使用命令：/bind 商户号\n"
                f"💡 Admin command: /bind MERCHANT_ID"
            )
        else:
            # 群聊
            welcome_text = (
                f"👋 欢迎使用 / Welcome to {settings.APP_NAME}！\n\n"
                f"🔐 此群尚未绑定商户账号\n"
                f"🔐 This group hasn't bound a merchant account yet\n\n"
                f"📞 请联系管理员在此群中执行绑定\n"
                f"📞 Please contact administrator to bind in this group\n\n"
                f"💡 管理员使用命令：/bind 商户号\n"
                f"💡 Admin command: /bind MERCHANT_ID"
            )
        
        await update.message.reply_text(welcome_text)
    else:
        # 已注册用户，加载语言偏好
        set_language(user.id, merchant.language)
        lang = merchant.language
        
        # 根据语言显示欢迎信息
        if lang == 'en':
            welcome_text = (
                f"👋 Welcome back, {merchant.full_name}!\n\n"
                f"🏪 Merchant Name: {merchant.merchant_name}\n"
                f"💰 Current Balance: ${merchant.available_balance:,.2f}\n\n"
                "Please select a function:"
            )
        else:
            welcome_text = (
                f"👋 欢迎回来，{merchant.full_name}！\n\n"
                f"🏪 商户名称：{merchant.merchant_name}\n"
                f"💰 当前余额：¥{merchant.available_balance:,.2f}\n\n"
                "请选择您需要的功能："
            )
        
        # 根据角色显示不同的菜单
        if merchant.can_broadcast():
            keyboard = get_admin_menu_keyboard()
        else:
            keyboard = get_main_menu_keyboard()
        
        await update.message.reply_text(welcome_text, reply_markup=keyboard)


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示用户的 Telegram ID"""
    user = update.effective_user
    
    is_admin = settings.is_admin(user.id)
    is_super_admin = settings.is_super_admin(user.id)
    
    user_id_str = escape(str(user.id))
    username_str = escape(f"@{user.username}" if user.username else "未设置")
    first_name_str = escape(user.first_name or "")
    last_name_str = escape(user.last_name or "")

    id_text = (
        "🆔 您的 Telegram 信息\n\n"
        f"👤 ID: <code>{user_id_str}</code>\n"
        f"📝 用户名: <code>{username_str}</code>\n"
        f"🏷️ 名字: {first_name_str} {last_name_str}\n\n"
    )
    
    if is_super_admin:
        id_text += "👑 权限: 超级管理员\n\n"
    elif is_admin:
        id_text += "🔑 权限: 管理员\n\n"
    else:
        id_text += "👤 权限: 普通用户\n\n"
    
    id_text += (
        "💡 如何成为管理员？\n"
        f"将您的 ID <code>{user_id_str}</code> 添加到服务器的\n"
        f".env 文件中的 <code>ADMIN_USER_IDS</code>\n"
    )
    
    await update.message.reply_text(id_text, parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_text = (
        f"📖 {settings.APP_NAME} 使用帮助\n\n"
        
        "🔹 基础功能：\n"
        "/start - 启动机器人\n"
        "/help - 显示帮助信息\n"
        "/myid - 查看我的 Telegram ID\n"
        "/balance - 查询账户余额\n"
        "/order <订单号> - 查询订单\n"
        "/history - 查看交易历史\n"
        "/upload - 上传图片识别订单\n"
        "/reset - 重置账号（删除所有数据）\n"
        "/cancel - 取消当前操作\n\n"
        
        "💰 余额查询：\n"
        "• 实时查看可用余额和冻结金额\n"
        "• 查看最近的交易记录\n\n"
        
        "📸 图片识别：\n"
        "• 支持上传订单截图\n"
        "• 自动识别订单号并查询\n"
        "• 支持多种订单格式\n\n"
        
        "📋 订单管理：\n"
        "• 查看订单列表和详情\n"
        "• 跟踪订单状态\n"
        "• 查询物流信息\n\n"
    )
    
    # 管理员额外帮助
    if settings.is_admin(update.effective_user.id):
        help_text += (
            "👑 管理员功能：\n"
            "/broadcast - 发送广播消息\n"
            "/stats - 查看数据统计\n"
            "/merchants - 管理商户\n\n"
        )
    
    help_text += (
        "❓ 遇到问题？\n"
        "请联系客服或查看在线文档。"
    )
    
    await update.message.reply_text(help_text)


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /balance 命令"""
    user = update.effective_user
    chat = update.effective_chat
    lang = get_language(user.id)
    
    try:
        # 获取商户信息（使用聊天ID）
        merchant_service = MerchantService()
        merchant = await merchant_service.get_by_telegram_id(chat.id)
        
        if not merchant:
            msg = get_text("not_registered", lang)
            await update.message.reply_text(msg)
            return
        
        # 发送查询中提示
        loading_msg = get_text("querying", lang) if lang == "en" else "⏳ 查询中，请稍候..."
        status_message = await update.message.reply_text(loading_msg)
        
        try:
            # 调用后端 API 查询余额
            from app.utils.api_client import api_client
            result = await api_client.query_balance(merchant.merchant_code)
            
            # 删除状态消息
            try:
                await status_message.delete()
            except Exception:
                pass  # 忽略删除消息失败
            
            # 处理响应
            if result.get("code") == 200:
                balance = result.get("balance", "0")
                use_balance = result.get("use_balance", "0")
                frozen_balance = result.get("frozen_balance", "0")
                
                if lang == "en":
                    balance_text = (
                        f"💰 Balance Query\n\n"
                        f"🏪 Merchant: {merchant.merchant_name}\n"
                        f"📊 Status: {'✅ Active' if merchant.is_active else '❌ Frozen'}\n\n"
                        f"💵 Available: ₹{use_balance}\n"
                        f"🔒 Frozen: ₹{frozen_balance}\n"
                        f"💎 Total: ₹{balance}\n"
                    )
                else:
                    balance_text = (
                        f"💰 余额查询\n\n"
                        f"🏪 商户：{merchant.merchant_name}\n"
                        f"📊 账户状态：{'✅ 正常' if merchant.is_active else '❌ 已冻结'}\n\n"
                        f"💵 可用余额：₹{use_balance}\n"
                        f"🔒 冻结金额：₹{frozen_balance}\n"
                f"💎 总余额：₹{balance}\n"
                    )
                
                await update.message.reply_text(balance_text)
            else:
                error_msg = result.get("msg", "Unknown error")
                error_code = result.get("code", 500)
                
                if lang == "en":
                    error_text = f"❌ Query failed\n\n"
                    if error_code == 503:
                        error_text += "🔌 Cannot connect to backend service\n"
                        error_text += "Please contact administrator"
                    elif error_code == 504:
                        error_text += "⏱️ Request timeout\n"
                        error_text += "Please try again later"
                    else:
                        error_text += f"Error: {error_msg}"
                    
                    await update.message.reply_text(error_text)
                else:
                    error_text = f"❌ 查询失败\n\n"
                    if error_code == 503:
                        error_text += "🔌 无法连接到后端服务\n"
                        error_text += "请联系管理员检查后端服务状态"
                    elif error_code == 504:
                        error_text += "⏱️ 请求超时\n"
                        error_text += "请稍后重试"
                    else:
                        error_text += f"错误信息：{error_msg}"
                    
                    await update.message.reply_text(error_text)
                    
        except Exception as api_error:
            logger.exception(f"余额查询 API 调用失败: {api_error}")
            
            # 确保删除状态消息
            try:
                await status_message.delete()
            except Exception:
                pass
            
            # 发送友好的错误消息
            if lang == "en":
                await update.message.reply_text(
                    "❌ Query failed\n\n"
                    "System error occurred\n"
                    "Please try again later or contact administrator"
                )
            else:
                await update.message.reply_text(
                    "❌ 查询失败\n\n"
                    "系统发生错误\n"
                    "请稍后重试或联系管理员"
                )
                
    except Exception as e:
        logger.exception(f"处理 /balance 命令时发生错误: {e}")
        
        # 确保机器人不会崩溃
        try:
            if lang == "en":
                await update.message.reply_text(
                    "❌ An error occurred\n\n"
                    "Please try again or use /help to see available commands"
                )
            else:
                await update.message.reply_text(
                    "❌ 发生错误\n\n"
                    "请重试或使用 /help 查看可用命令"
                )
        except Exception:
            pass  # 如果连发送消息都失败，就放弃


async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /order 命令 - 订单查询"""
    user = update.effective_user
    chat = update.effective_chat
    lang = get_language(user.id)
    
    # 获取商户信息（使用聊天ID）
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(chat.id)
    
    if not merchant:
        msg = get_text("not_registered", lang)
        await update.message.reply_text(msg)
        return
    
    # 检查是否带订单号参数
    if context.args and len(context.args) >= 1:
        # 直接查询订单
        order_no = context.args[0]
        from app.bot.handlers import handle_order_search
        await handle_order_search(update, context, order_no)
    else:
        # 显示使用帮助
        if lang == "en":
            order_text = (
                "📋 Order Query\n\n"
                "📝 Usage:\n"
                "<code>/order ORDER_NUMBER</code>\n\n"
                "📋 Example:\n"
                "<code>/order ORDER123456</code>\n\n"
                "💡 You can also:\n"
                "• Send order number directly\n"
                "• Send order screenshot (with caption for faster query)\n"
                "• Send image + order number as caption\n\n"
                "🔙 Send /cancel to cancel"
            )
        else:
            order_text = (
                "📋 订单查询\n\n"
                "📝 使用方法：\n"
                "<code>/order 订单号</code>\n\n"
                "📋 示例：\n"
                "<code>/order ORDER123456</code>\n\n"
                "💡 您也可以：\n"
                "• 直接发送订单号文本\n"
                "• 发送订单截图（配文字说明更快）\n"
                "• 发送图片 + 订单号作为图片说明\n\n"
                "🔙 发送 /cancel 取消查询"
            )
        
        # 设置等待订单号状态
        context.user_data['awaiting_order_id'] = True
        await update.message.reply_text(order_text, parse_mode='HTML')


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /history 命令"""
    user = update.effective_user
    chat = update.effective_chat
    
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(chat.id)
    
    if not merchant:
        await update.message.reply_text("❌ 您还未注册，请先使用 /start 命令注册")
        return
    
    # 获取交易历史
    balance_service = BalanceService()
    transactions = await balance_service.get_transaction_history(merchant.id, limit=10)
    
    if not transactions:
        await update.message.reply_text("📊 暂无交易记录")
        return
    
    history_text = "📊 交易历史记录\n\n"
    
    for idx, trans in enumerate(transactions, 1):
        type_emoji = {
            'recharge': '💰',
            'withdraw': '💸',
            'payment': '💳',
            'refund': '🔄',
        }.get(trans['transaction_type'], '📝')
        
        history_text += (
            f"{idx}. {type_emoji} {trans['description']}\n"
            f"   金额：¥{trans['amount']:,.2f}\n"
            f"   时间：{trans['created_at']}\n\n"
        )
    
    await update.message.reply_text(history_text)


async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /upload 命令"""
    user = update.effective_user
    chat = update.effective_chat
    
    # 获取用户语言
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(chat.id)
    
    if not merchant:
        await update.message.reply_text("❌ 您还未注册，请先使用 /start 命令注册")
        return
    
    lang = merchant.language
    
    if lang == 'en':
        upload_text = (
            "📸 Image Recognition\n\n"
            "Please upload order screenshot, I will automatically recognize order number and query order information.\n\n"
            "Supported formats:\n"
            "• JPG/JPEG\n"
            "• PNG\n"
            "• WebP\n\n"
            "💡 Tips:\n"
            "• Ensure image is clear\n"
            "• Order number should be fully visible\n"
            "• Image size should not exceed 10MB\n\n"
            "📤 Ready to receive your image..."
        )
    else:
        upload_text = (
            "📸 图片识别功能\n\n"
            "请上传订单截图，我将自动识别订单号并为您查询订单信息。\n\n"
            "支持的图片格式：\n"
            "• JPG/JPEG\n"
            "• PNG\n"
            "• WebP\n\n"
            "💡 提示：\n"
            "• 请确保图片清晰\n"
            "• 订单号要完整可见\n"
            "• 图片大小不超过10MB\n\n"
            "📤 准备接收您的图片..."
        )
    
    await update.message.reply_text(upload_text)
    # 设置等待图片上传标志
    context.user_data["awaiting_image_upload"] = True


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /cancel 命令"""
    user = update.effective_user
    chat = update.effective_chat
    
    # 获取用户语言
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(chat.id)
    lang = merchant.language if merchant else 'zh'
    
    # 检查当前状态
    has_state = bool(context.user_data)
    
    context.user_data.clear()
    
    if lang == 'en':
        if has_state:
            message = (
                "❌ Operation cancelled\n\n"
                "Current operation has been cancelled.\n"
                "Use /start to return to main menu."
            )
        else:
            message = (
                "ℹ️ No active operation\n\n"
                "Use /start to return to main menu."
            )
    else:
        if has_state:
            message = (
                "❌ 操作已取消\n\n"
                "当前操作已取消。\n"
                "使用 /start 返回主菜单。"
            )
        else:
            message = (
                "ℹ️ 没有进行中的操作\n\n"
                "使用 /start 返回主菜单。"
            )
    
    await update.message.reply_text(message)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /reset 命令 - 重置账号"""
    user = update.effective_user
    chat = update.effective_chat
    
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(chat.id)
    
    if not merchant:
        await update.message.reply_text(
            "ℹ️ 您还未注册\n\n"
            "请使用 /start 进行注册。"
        )
        return
    
    # 确认删除
    if not context.user_data.get("confirm_reset"):
        context.user_data["confirm_reset"] = True
        await update.message.reply_text(
            "⚠️ 警告：重置账号将删除所有数据！\n\n"
            f"当前账号信息：\n"
            f"🏪 商户名称：{merchant.merchant_name}\n"
            f"🆔 商户编号：{merchant.merchant_code}\n"
            f"💰 当前余额：¥{merchant.available_balance:,.2f}\n\n"
            "⚠️ 删除后将无法恢复！\n\n"
            "如果确认要重置，请再次发送 /reset\n"
            "如果取消，请发送 /cancel"
        )
        return
    
    # 执行删除
    try:
        from sqlalchemy import delete
        from app.database.session import AsyncSessionLocal
        from app.models.merchant import Merchant
        
        async with AsyncSessionLocal() as session:
            # 删除商户记录（会级联删除订单和交易记录）
            await session.execute(
                delete(Merchant).where(Merchant.telegram_id == chat.id)
            )
            await session.commit()
        
        context.user_data.clear()
        
        await update.message.reply_text(
            "✅ 账号已重置！\n\n"
            "所有数据已删除。\n\n"
            "您可以使用 /start 重新注册。"
        )
        
        logger.info(f"用户 {user.id} 重置了账号")
        
    except Exception as e:
        logger.error(f"重置账号失败: {e}")
        context.user_data.clear()
        await update.message.reply_text(
            "❌ 重置失败\n\n"
            "发生了错误，请稍后重试或联系管理员。"
        )


# 管理员命令

async def bind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /bind 命令 - 管理员绑定商户"""
    user = update.effective_user
    chat = update.effective_chat
    
    # 检查管理员权限
    if not settings.is_admin(user.id):
        await update.message.reply_text(
            "❌ 权限不足\n\n"
            "只有管理员可以使用此命令。"
        )
        return
    
    # 显示绑定指引
    help_text = (
        "👑 管理员 - 绑定商户\n\n"
        "📝 使用方法：\n"
        "<code>/bind 商户号</code>\n\n"
        "📋 示例：\n"
        "<code>/bind MERCHANT001</code>\n\n"
        "💡 说明：\n"
        "• 在私聊中执行：绑定当前用户\n"
        "• 在群聊中执行：绑定整个群\n"
        "• 商户号：后端系统中的商户编号\n"
        "• 如果已绑定，会更新为新的商户号\n\n"
        f"📍 当前聊天类型：{'私聊' if chat.type == 'private' else '群聊'}\n"
        f"📍 当前聊天ID：<code>{chat.id}</code>"
    )
    
    # 检查是否带参数
    if context.args and len(context.args) >= 1:
        # 直接处理绑定
        merchant_code = context.args[0]
        await handle_bind_merchant(update, context, merchant_code)
    else:
        await update.message.reply_text(help_text, parse_mode='HTML')


async def handle_bind_merchant(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               merchant_code: str):
    """处理商户绑定 - 绑定当前聊天（用户或群组）"""
    try:
        chat = update.effective_chat
        user = update.effective_user
        
        # 验证商户号
        if len(merchant_code) < 3:
            await update.message.reply_text(
                "❌ 商户号格式错误\n\n"
                "商户号至少需要3个字符"
            )
            return
        
        # 发送处理中提示
        status_msg = await update.message.reply_text("⏳ 正在绑定商户...")
        
        # 使用聊天ID作为标识（私聊或群聊）
        chat_id = chat.id
        
        # 获取聊天信息
        if chat.type == 'private':
            # 私聊：使用用户信息
            chat_name = chat.first_name or chat.username or f"User {chat_id}"
            chat_type_text = "私聊用户"
        else:
            # 群聊：使用群组信息
            chat_name = chat.title or f"Group {chat_id}"
            chat_type_text = "群聊"
        
        merchant_service = MerchantService()
        
        # 检查是否已绑定（使用 chat_id）
        existing_merchant = await merchant_service.get_by_telegram_id(chat_id)
        
        if existing_merchant:
            # 更新现有绑定
            old_code = existing_merchant.merchant_code
            existing_merchant.merchant_code = merchant_code
            existing_merchant.merchant_name = merchant_code  # 可以后续从后端API获取
            
            from app.database.session import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                session.add(existing_merchant)
                await session.commit()
            
            await status_msg.edit_text(
                f"✅ 商户绑定已更新！\n\n"
                f"📍 {chat_type_text}: {chat_name}\n"
                f"🆔 聊天ID: <code>{chat_id}</code>\n"
                f"🏪 原商户号: {old_code}\n"
                f"🏪 新商户号: {merchant_code}\n\n"
                f"📢 {'用户' if chat.type == 'private' else '群成员'}需要重新发送 /start 以刷新信息",
                parse_mode='HTML'
            )
            
            # 如果是私聊，通知用户
            if chat.type == 'private' and chat_id != user.id:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"✅ 商户绑定已更新\n\n"
                            f"🏪 新商户号: {merchant_code}\n\n"
                            f"请发送 /start 查看详情"
                        )
                    )
                except Exception as e:
                    logger.warning(f"无法通知聊天 {chat_id}: {e}")
        else:
            # 创建新绑定
            # 获取聊天的详细信息
            try:
                chat_info = await context.bot.get_chat(chat_id)
                username = getattr(chat_info, 'username', None)
                first_name = getattr(chat_info, 'first_name', None)
                last_name = getattr(chat_info, 'last_name', None)
            except Exception:
                username = None
                first_name = chat_name
                last_name = None
            
            new_merchant = await merchant_service.create_merchant(
                telegram_id=chat_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                merchant_code=merchant_code,
                merchant_name=merchant_code  # 可以后续从后端API获取
            )
            
            await status_msg.edit_text(
                f"✅ 商户绑定成功！\n\n"
                f"📍 {chat_type_text}: {chat_name}\n"
                f"🆔 聊天ID: <code>{chat_id}</code>\n"
                f"🏪 商户号: {merchant_code}\n\n"
                f"📢 {'用户' if chat.type == 'private' else '群成员'}可以发送 /start 开始使用",
                parse_mode='HTML'
            )
            
            # 如果是私聊且不是管理员自己，通知用户
            if chat.type == 'private' and chat_id != user.id:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"✅ 您的账号已被管理员绑定\n\n"
                            f"🏪 商户号: {merchant_code}\n\n"
                            f"请发送 /start 开始使用"
                        )
                    )
                except Exception as e:
                    logger.warning(f"无法通知聊天 {chat_id}: {e}")
        
    except Exception as e:
        logger.exception(f"绑定商户失败: {e}")
        await update.message.reply_text(
            f"❌ 绑定失败\n\n"
            f"错误信息: {str(e)}\n\n"
            f"请检查参数是否正确"
        )


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /broadcast 命令（管理员）"""
    user = update.effective_user
    
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此命令")
        return
    
    broadcast_text = (
        "📢 广播消息功能\n\n"
        "🔹 使用方法：\n"
        "在下一条消息中输入要广播的内容，\n"
        "Bot 将发送给所有已注册的商户。\n\n"
        "支持的格式：\n"
        "• 文字消息\n"
        "• 图片（带文字说明）\n"
        "• 链接\n\n"
        "💡 提示：发送 /cancel 可以取消广播"
    )
    
    await update.message.reply_text(broadcast_text)
    context.user_data["awaiting_broadcast"] = True


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /stats 命令（管理员）"""
    user = update.effective_user
    
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此命令")
        return
    
    # TODO: 实现统计功能
    stats_text = (
        "📊 系统统计数据\n\n"
        "👥 总商户数：123\n"
        "✅ 活跃商户：98\n"
        "📋 今日订单：45\n"
        "💰 今日交易额：¥12,345.67\n\n"
        "📈 本周趋势：\n"
        "订单量：↑ 15%\n"
        "交易额：↑ 23%\n"
    )
    
    await update.message.reply_text(stats_text)


async def merchants_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /merchants 命令（管理员）"""
    user = update.effective_user
    
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此命令")
        return
    
    # TODO: 实现商户列表功能
    await update.message.reply_text("👥 商户管理功能开发中...")

