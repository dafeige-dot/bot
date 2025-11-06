"""
回调查询处理模块
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
from app.config import settings
from app.bot.language import language_callback


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    user = update.effective_user
    
    await query.answer()
    
    callback_data = query.data
    logger.info(f"用户 {user.id} 点击了按钮: {callback_data}")
    
    # 语言切换
    if callback_data.startswith("lang_"):
        lang_code = callback_data.split("_")[1]
        await language_callback(query, user.id, lang_code)
        return
    
    # 路由到不同的处理函数
    if callback_data == "main_menu":
        await show_main_menu(query, context)
    elif callback_data == "admin_menu":
        await show_admin_menu(query, context)
    elif callback_data == "balance":
        await show_balance(query, context)
    elif callback_data == "refresh_balance":
        await refresh_balance(query, context)
    elif callback_data == "orders":
        await show_orders(query, context)
    elif callback_data.startswith("orders_page_"):
        page = int(callback_data.split("_")[-1])
        await show_orders(query, context, page)
    elif callback_data == "history":
        await show_history(query, context)
    elif callback_data == "upload":
        await prompt_upload(query, context)
    elif callback_data == "help":
        await show_help(query, context)
    elif callback_data == "settings":
        await show_settings(query, context)
    elif callback_data == "admin_broadcast":
        await show_broadcast_menu(query, context)
    elif callback_data == "admin_merchants":
        await show_merchants(query, context)
    elif callback_data == "admin_stats":
        await show_stats(query, context)
    elif callback_data == "cancel":
        await handle_cancel(query, context)
    else:
        await query.edit_message_text("❓ 未知操作")


async def show_main_menu(query, context):
    """显示主菜单"""
    user = query.from_user
    
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    if not merchant:
        await query.edit_message_text("❌ 请先使用 /start 命令注册")
        return
    
    menu_text = (
        f"🏪 主菜单\n\n"
        f"商户：{merchant.merchant_name}\n"
        f"余额：¥{merchant.available_balance:,.2f}\n\n"
        "请选择功能："
    )
    
    keyboard = get_admin_menu_keyboard() if merchant.can_broadcast() else get_main_menu_keyboard()
    
    await query.edit_message_text(menu_text, reply_markup=keyboard)


async def show_admin_menu(query, context):
    """显示管理员菜单"""
    user = query.from_user
    
    if not settings.is_admin(user.id):
        await query.edit_message_text("❌ 您没有权限访问管理员菜单")
        return
    
    menu_text = "👑 管理员菜单\n\n请选择管理功能："
    
    await query.edit_message_text(menu_text, reply_markup=get_admin_menu_keyboard())


async def show_balance(query, context):
    """显示余额"""
    user = query.from_user
    
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    if not merchant:
        await query.edit_message_text("❌ 请先注册")
        return
    
    balance_service = BalanceService()
    balance_info = await balance_service.get_balance(merchant.id)
    
    balance_text = (
        f"💰 账户余额\n\n"
        f"商户：{merchant.merchant_name}\n"
        f"状态：{'✅ 正常' if merchant.is_active else '❌ 已冻结'}\n\n"
        f"💵 可用余额：¥{balance_info['available']:,.2f}\n"
        f"🔒 冻结金额：¥{balance_info['frozen']:,.2f}\n"
        f"💎 总余额：¥{balance_info['total']:,.2f}\n\n"
        f"📅 更新时间：{balance_info['query_time']}"
    )
    
    await query.edit_message_text(balance_text, reply_markup=get_balance_keyboard())


async def refresh_balance(query, context):
    """刷新余额"""
    await query.answer("🔄 正在刷新...")
    await show_balance(query, context)


async def show_orders(query, context, page: int = 1):
    """显示订单列表"""
    await query.edit_message_text("📋 订单列表功能开发中...")


async def show_history(query, context):
    """显示交易历史"""
    await query.edit_message_text("📊 交易历史功能开发中...")


async def prompt_upload(query, context):
    """提示上传图片"""
    user = query.from_user
    
    # 获取用户语言
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    if merchant and merchant.language == 'en':
        upload_text = (
            "📸 Image Recognition\n\n"
            "Please upload order screenshot, I will recognize the order number for you.\n\n"
            "💡 Tips:\n"
            "• Image should be clear\n"
            "• Order number should be complete\n"
            "• Size should not exceed 10MB\n\n"
            "📤 Ready to receive your image..."
        )
    else:
        upload_text = (
            "📸 图片识别\n\n"
            "请上传订单截图，我将为您识别订单号。\n\n"
            "💡 提示：\n"
            "• 图片要清晰\n"
            "• 订单号要完整\n"
            "• 大小不超过10MB\n\n"
            "📤 准备接收您的图片..."
        )
    
    await query.edit_message_text(upload_text)
    # 设置等待图片上传标志
    context.user_data["awaiting_image_upload"] = True


async def show_help(query, context):
    """显示帮助"""
    help_text = (
        "📖 使用帮助\n\n"
        "基础功能：\n"
        "• 余额查询\n"
        "• 订单查看\n"
        "• 图片识别\n"
        "• 交易历史\n\n"
        "详细帮助请使用 /help 命令"
    )
    
    await query.edit_message_text(help_text)


async def show_settings(query, context):
    """显示设置"""
    await query.edit_message_text("⚙️ 设置功能开发中...")


async def show_broadcast_menu(query, context):
    """显示广播菜单"""
    user = query.from_user
    
    if not settings.is_admin(user.id):
        await query.edit_message_text("❌ 无权限")
        return
    
    broadcast_text = "📢 广播消息\n\n请选择广播类型："
    
    await query.edit_message_text(broadcast_text, reply_markup=get_broadcast_keyboard())


async def show_merchants(query, context):
    """显示商户列表"""
    await query.edit_message_text("👥 商户列表功能开发中...")


async def show_stats(query, context):
    """显示统计数据"""
    await query.edit_message_text("📊 统计功能开发中...")


async def handle_cancel(query, context):
    """取消操作"""
    context.user_data.clear()
    await query.edit_message_text("❌ 操作已取消")

