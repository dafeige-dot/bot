"""
键盘布局模块
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_main_menu_keyboard():
    """获取主菜单键盘"""
    keyboard = [
        [
            InlineKeyboardButton("💰 查询余额", callback_data="balance"),
            InlineKeyboardButton("📋 我的订单", callback_data="orders"),
        ],
        [
            InlineKeyboardButton("📸 上传图片识别", callback_data="upload"),
            InlineKeyboardButton("📊 交易历史", callback_data="history"),
        ],
        [
            InlineKeyboardButton("❓ 帮助", callback_data="help"),
            InlineKeyboardButton("⚙️ 设置", callback_data="settings"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_menu_keyboard():
    """获取管理员菜单键盘"""
    keyboard = [
        [
            InlineKeyboardButton("📢 发送广播", callback_data="admin_broadcast"),
            InlineKeyboardButton("👥 商户列表", callback_data="admin_merchants"),
        ],
        [
            InlineKeyboardButton("📊 数据统计", callback_data="admin_stats"),
            InlineKeyboardButton("📄 导出数据", callback_data="admin_export"),
        ],
        [
            InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_balance_keyboard():
    """获取余额查询键盘"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 刷新余额", callback_data="refresh_balance"),
            InlineKeyboardButton("📊 交易记录", callback_data="transactions"),
        ],
        [
            InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_order_list_keyboard(page: int = 1, has_next: bool = False):
    """获取订单列表键盘"""
    keyboard = []
    
    # 翻页按钮
    page_buttons = []
    if page > 1:
        page_buttons.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"orders_page_{page-1}"))
    if has_next:
        page_buttons.append(InlineKeyboardButton("➡️ 下一页", callback_data=f"orders_page_{page+1}"))
    
    if page_buttons:
        keyboard.append(page_buttons)
    
    # 操作按钮
    keyboard.append([
        InlineKeyboardButton("🔄 刷新", callback_data=f"orders_page_{page}"),
        InlineKeyboardButton("🔍 搜索订单", callback_data="search_order"),
    ])
    
    keyboard.append([
        InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu"),
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_order_detail_keyboard(order_id: int):
    """获取订单详情键盘"""
    keyboard = [
        [
            InlineKeyboardButton("📋 查看物流", callback_data=f"order_logistics_{order_id}"),
            InlineKeyboardButton("💬 联系客服", callback_data=f"order_support_{order_id}"),
        ],
        [
            InlineKeyboardButton("🔙 返回订单列表", callback_data="orders"),
            InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_broadcast_keyboard():
    """获取广播消息键盘"""
    keyboard = [
        [
            InlineKeyboardButton("📢 全员广播", callback_data="broadcast_all"),
            InlineKeyboardButton("👥 分组广播", callback_data="broadcast_group"),
        ],
        [
            InlineKeyboardButton("📝 草稿箱", callback_data="broadcast_drafts"),
            InlineKeyboardButton("📋 历史记录", callback_data="broadcast_history"),
        ],
        [
            InlineKeyboardButton("🔙 返回", callback_data="admin_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard():
    """获取取消键盘"""
    keyboard = [
        [InlineKeyboardButton("❌ 取消操作", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(action: str):
    """获取确认键盘"""
    keyboard = [
        [
            InlineKeyboardButton("✅ 确认", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ 取消", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_simple_reply_keyboard(buttons: list, one_time: bool = True):
    """获取简单的回复键盘"""
    keyboard = [[button] for button in buttons]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=one_time,
    )

