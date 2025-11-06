"""
命令处理模块
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from app.bot.keyboards import (
    get_main_menu_keyboard,
    get_admin_menu_keyboard,
    get_balance_keyboard,
    get_broadcast_keyboard,
)
from app.services.merchant import MerchantService
from app.services.balance import BalanceService
from app.services.order import OrderService
from app.config import settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user = update.effective_user
    logger.info(f"用户 {user.id} ({user.username}) 启动了机器人")
    
    # 检查用户是否已注册
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    if not merchant:
        # 新用户，引导注册
        welcome_text = (
            f"👋 欢迎使用 {settings.APP_NAME}！\n\n"
            f"您好，{user.first_name}！\n\n"
            "🔐 请输入您的商户验证码进行注册：\n"
            "（验证码可从管理员处获取）"
        )
        await update.message.reply_text(welcome_text)
        context.user_data["awaiting_merchant_code"] = True
    else:
        # 已注册用户
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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_text = (
        f"📖 {settings.APP_NAME} 使用帮助\n\n"
        
        "🔹 基础功能：\n"
        "/start - 启动机器人\n"
        "/help - 显示帮助信息\n"
        "/balance - 查询账户余额\n"
        "/orders - 查看订单列表\n"
        "/history - 查看交易历史\n"
        "/upload - 上传图片识别订单\n"
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
    
    # 获取商户信息
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    if not merchant:
        await update.message.reply_text("❌ 您还未注册，请先使用 /start 命令注册")
        return
    
    # 获取余额信息
    balance_service = BalanceService()
    balance_info = await balance_service.get_balance(merchant.id)
    
    balance_text = (
        f"💰 余额查询\n\n"
        f"🏪 商户：{merchant.merchant_name}\n"
        f"📊 账户状态：{'✅ 正常' if merchant.is_active else '❌ 已冻结'}\n\n"
        f"💵 可用余额：¥{balance_info['available']:,.2f}\n"
        f"🔒 冻结金额：¥{balance_info['frozen']:,.2f}\n"
        f"💎 总余额：¥{balance_info['total']:,.2f}\n\n"
        f"📅 查询时间：{balance_info['query_time']}\n"
    )
    
    await update.message.reply_text(
        balance_text,
        reply_markup=get_balance_keyboard()
    )


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /orders 命令"""
    user = update.effective_user
    
    # 获取商户信息
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    if not merchant:
        await update.message.reply_text("❌ 您还未注册，请先使用 /start 命令注册")
        return
    
    # 获取订单列表
    order_service = OrderService()
    orders = await order_service.get_merchant_orders(merchant.id, page=1, page_size=10)
    
    if not orders['items']:
        await update.message.reply_text(
            "📋 暂无订单\n\n"
            "您还没有任何订单记录。"
        )
        return
    
    # 构建订单列表文本
    order_text = f"📋 订单列表 (第{orders['page']}页)\n\n"
    
    for idx, order in enumerate(orders['items'], 1):
        status_emoji = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'cancelled': '❌',
        }.get(order['order_status'], '❓')
        
        order_text += (
            f"{idx}. {status_emoji} {order['order_no']}\n"
            f"   金额：¥{order['amount']:,.2f}\n"
            f"   状态：{order['order_status']}\n"
            f"   时间：{order['created_at']}\n\n"
        )
    
    order_text += f"共 {orders['total']} 条订单"
    
    await update.message.reply_text(order_text)


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /history 命令"""
    user = update.effective_user
    
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
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
        "• 图片大小不超过10MB"
    )
    
    await update.message.reply_text(upload_text)
    context.user_data["awaiting_image"] = True


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /cancel 命令"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ 操作已取消\n\n"
        "您可以使用 /start 返回主菜单。"
    )


# 管理员命令

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /broadcast 命令（管理员）"""
    user = update.effective_user
    
    if not settings.is_admin(user.id):
        await update.message.reply_text("❌ 您没有权限使用此命令")
        return
    
    broadcast_text = (
        "📢 广播消息管理\n\n"
        "请选择广播类型："
    )
    
    await update.message.reply_text(
        broadcast_text,
        reply_markup=get_broadcast_keyboard()
    )


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

