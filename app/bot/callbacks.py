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
    
    callback_data = query.data
    logger.info(f"用户 {user.id} 点击了按钮: {callback_data}")
    
    # 定向群组广播回调（需要特殊处理answer）
    if callback_data.startswith("dxgb_"):
        await handle_dxgb_callback(query, context, user)
        return
    
    await query.answer()
    
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



async def handle_dxgb_callback(query, context, user):
    """处理定向群组广播的回调"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    if not settings.is_admin(user.id):
        await query.answer("❌ 无权限", show_alert=True)
        return
    
    callback_data = query.data
    
    # 取消操作
    if callback_data == "dxgb_cancel":
        context.user_data.pop("dxgb_selected", None)
        context.user_data.pop("dxgb_merchants", None)
        context.user_data.pop("awaiting_dxgb_message", None)
        await query.answer("已取消")
        await query.edit_message_text("❌ 定向广播已取消")
        return
    
    merchants = context.user_data.get("dxgb_merchants", {})
    selected = context.user_data.get("dxgb_selected", [])
    
    if not merchants:
        await query.answer("❌ 会话已过期，请重新使用 /dxgb 命令", show_alert=True)
        return
    
    # 全选
    if callback_data == "dxgb_select_all":
        if len(selected) == len(merchants):
            # 已全选，则取消全选
            context.user_data["dxgb_selected"] = []
            await query.answer("已取消全选")
        else:
            context.user_data["dxgb_selected"] = list(merchants.keys())
            await query.answer("已全选")
        selected = context.user_data["dxgb_selected"]
    
    # 确认发送
    elif callback_data == "dxgb_confirm":
        if not selected:
            await query.answer("❌ 请至少选择一个群组", show_alert=True)
            return
        
        # 进入等待消息状态
        context.user_data["awaiting_dxgb_message"] = True
        await query.answer()
        
        selected_names = [merchants[tid] for tid in selected if tid in merchants]
        await query.edit_message_text(
            f"✅ 已选择 {len(selected)} 个群组：\n\n"
            f"{'、'.join(selected_names[:5])}"
            f"{'...' if len(selected_names) > 5 else ''}\n\n"
            f"📝 请发送要广播的内容（文字或图片）：\n\n"
            f"💡 发送 /cancel 取消操作"
        )
        return
    
    # 选择/取消选择单个群组
    elif callback_data.startswith("dxgb_select_"):
        try:
            group_id = int(callback_data.replace("dxgb_select_", ""))
            if group_id in selected:
                selected.remove(group_id)
                await query.answer("已取消选择")
            else:
                selected.append(group_id)
                await query.answer("已选择")
            context.user_data["dxgb_selected"] = selected
        except ValueError:
            await query.answer("❌ 无效的群组ID", show_alert=True)
            return
    
    # 更新按钮显示
    buttons = []
    row = []
    merchant_list = list(merchants.items())
    for i, (tid, name) in enumerate(merchant_list):
        display_name = name[:12] + "..." if len(name) > 12 else name
        # 选中的显示 ✓
        prefix = "✓ " if tid in selected else "📢 "
        btn = InlineKeyboardButton(
            f"{prefix}{display_name}",
            callback_data=f"dxgb_select_{tid}"
        )
        row.append(btn)
        
        if len(row) == 2 or i == len(merchant_list) - 1:
            buttons.append(row)
            row = []
    
    # 添加操作按钮
    buttons.append([
        InlineKeyboardButton(
            "☑️ 取消全选" if len(selected) == len(merchants) else "✅ 全选",
            callback_data="dxgb_select_all"
        ),
        InlineKeyboardButton("❌ 取消", callback_data="dxgb_cancel")
    ])
    
    # 如果有选中的群组，显示确认按钮
    if selected:
        buttons.append([
            InlineKeyboardButton(f"📤 确认发送 ({len(selected)}个群组)", callback_data="dxgb_confirm")
        ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        f"📢 定向群组广播\n\n"
        f"📋 共 {len(merchants)} 个群组，已选择 {len(selected)} 个\n"
        f"请点击选择要发送广播的群组：\n\n"
        f"💡 提示：\n"
        f"• 点击群组名称选择/取消选择\n"
        f"• 选中的群组会显示 ✓ 标记\n"
        f"• 选择完成后点击「确认发送」",
        reply_markup=keyboard
    )
