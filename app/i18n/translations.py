"""
多语言翻译字典
"""

TRANSLATIONS = {
    # 通用
    'app_name': {
        'zh': '商户管理机器人',
        'en': 'Merchant Management Bot',
    },
    'welcome': {
        'zh': '👋 欢迎使用',
        'en': '👋 Welcome to',
    },
    'hello': {
        'zh': '您好',
        'en': 'Hello',
    },
    
    # 命令相关
    'cmd_start': {
        'zh': '开始使用机器人',
        'en': 'Start the bot',
    },
    'cmd_help': {
        'zh': '获取帮助信息',
        'en': 'Get help',
    },
    'cmd_balance': {
        'zh': '查询余额',
        'en': 'Check balance',
    },
    'cmd_orders': {
        'zh': '查询订单',
        'en': 'View orders',
    },
    'cmd_history': {
        'zh': '交易历史',
        'en': 'Transaction history',
    },
    'cmd_upload': {
        'zh': '上传图片识别订单',
        'en': 'Upload image to recognize order',
    },
    'cmd_language': {
        'zh': '切换语言',
        'en': 'Change language',
    },
    'cmd_myid': {
        'zh': '查看我的 Telegram ID',
        'en': 'View my Telegram ID',
    },
    'cmd_reset': {
        'zh': '重置账号',
        'en': 'Reset account',
    },
    'cmd_cancel': {
        'zh': '取消当前操作',
        'en': 'Cancel current operation',
    },
    
    # 注册相关
    'register_prompt': {
        'zh': '🔐 请输入商户验证码进行注册',
        'en': '🔐 Please enter merchant verification code to register',
    },
    'register_dev_hint': {
        'zh': '💡 开发模式提示：\n输入任意4位以上字符即可注册\n例如：TEST、1234、DEMO 等',
        'en': '💡 Dev mode tip:\nEnter any 4+ characters to register\nExample: TEST, 1234, DEMO',
    },
    'register_success': {
        'zh': '✅ 注册成功！',
        'en': '✅ Registration successful!',
    },
    'register_welcome': {
        'zh': '欢迎您',
        'en': 'Welcome',
    },
    'merchant_name': {
        'zh': '商户名称',
        'en': 'Merchant Name',
    },
    'merchant_code': {
        'zh': '商户编号',
        'en': 'Merchant Code',
    },
    'initial_balance': {
        'zh': '初始余额',
        'en': 'Initial Balance',
    },
    'register_failed': {
        'zh': '❌ 注册失败',
        'en': '❌ Registration failed',
    },
    
    # 余额相关
    'balance_query': {
        'zh': '💰 余额查询',
        'en': '💰 Balance Query',
    },
    'merchant': {
        'zh': '商户',
        'en': 'Merchant',
    },
    'account_status': {
        'zh': '账户状态',
        'en': 'Account Status',
    },
    'status_normal': {
        'zh': '正常',
        'en': 'Normal',
    },
    'status_frozen': {
        'zh': '已冻结',
        'en': 'Frozen',
    },
    'available_balance': {
        'zh': '可用余额',
        'en': 'Available Balance',
    },
    'frozen_amount': {
        'zh': '冻结金额',
        'en': 'Frozen Amount',
    },
    'total_balance': {
        'zh': '总余额',
        'en': 'Total Balance',
    },
    'query_time': {
        'zh': '查询时间',
        'en': 'Query Time',
    },
    
    # 订单相关
    'order_list': {
        'zh': '📋 订单列表',
        'en': '📋 Order List',
    },
    'no_orders': {
        'zh': '📋 暂无订单',
        'en': '📋 No orders',
    },
    'order_amount': {
        'zh': '金额',
        'en': 'Amount',
    },
    'order_status': {
        'zh': '状态',
        'en': 'Status',
    },
    'order_time': {
        'zh': '时间',
        'en': 'Time',
    },
    'total_orders': {
        'zh': '共',
        'en': 'Total',
    },
    'orders_count': {
        'zh': '条订单',
        'en': 'orders',
    },
    
    # 帮助信息
    'help_title': {
        'zh': '📖 使用帮助',
        'en': '📖 Help',
    },
    'help_basic': {
        'zh': '🔹 基础功能：',
        'en': '🔹 Basic Functions:',
    },
    'help_balance_desc': {
        'zh': '💰 余额查询：\n• 实时查看可用余额和冻结金额\n• 查看最近的交易记录',
        'en': '💰 Balance Query:\n• View available and frozen balance\n• View recent transactions',
    },
    'help_ocr_desc': {
        'zh': '📸 图片识别：\n• 支持上传订单截图\n• 自动识别订单号并查询\n• 支持多种订单格式',
        'en': '📸 Image Recognition:\n• Upload order screenshots\n• Auto recognize order numbers\n• Support multiple formats',
    },
    
    # 语言设置
    'language_select': {
        'zh': '🌍 语言设置\n\n请选择您的语言：',
        'en': '🌍 Language Settings\n\nPlease select your language:',
    },
    'language_changed': {
        'zh': '✅ 语言已切换为中文',
        'en': '✅ Language changed to English',
    },
    'chinese': {
        'zh': '🇨🇳 中文',
        'en': '🇨🇳 Chinese',
    },
    'english': {
        'zh': '🇺🇸 English',
        'en': '🇺🇸 English',
    },
    
    # 按钮文本
    'btn_balance': {
        'zh': '💰 查询余额',
        'en': '💰 Check Balance',
    },
    'btn_orders': {
        'zh': '📋 我的订单',
        'en': '📋 My Orders',
    },
    'btn_upload': {
        'zh': '📸 上传图片识别',
        'en': '📸 Upload Image',
    },
    'btn_history': {
        'zh': '📊 交易历史',
        'en': '📊 History',
    },
    'btn_help': {
        'zh': '❓ 帮助',
        'en': '❓ Help',
    },
    'btn_settings': {
        'zh': '⚙️ 设置',
        'en': '⚙️ Settings',
    },
    'btn_language': {
        'zh': '🌍 语言',
        'en': '🌍 Language',
    },
    
    # 错误消息
    'error_permission': {
        'zh': '❌ 您没有权限使用此命令',
        'en': '❌ You do not have permission to use this command',
    },
    'error_not_registered': {
        'zh': '❌ 您还未注册，请先使用 /start 命令注册',
        'en': '❌ Not registered. Please use /start to register',
    },
    'error_unknown': {
        'zh': '我不太明白您的意思。\n请使用 /help 查看可用命令。',
        'en': 'I don\'t understand.\nPlease use /help to see available commands.',
    },
    
    # 广播相关
    'broadcast_title': {
        'zh': '📢 广播消息功能',
        'en': '📢 Broadcast Message',
    },
    'broadcast_usage': {
        'zh': '🔹 使用方法：\n在下一条消息中输入要广播的内容，\nBot 将发送给所有已注册的商户。',
        'en': '🔹 Usage:\nEnter the message to broadcast in next message,\nBot will send to all registered merchants.',
    },
    'broadcast_preview': {
        'zh': '📢 广播消息预览：',
        'en': '📢 Broadcast Preview:',
    },
    'broadcast_confirm': {
        'zh': '确认发送吗？\n• 回复 \'确认\' 开始发送\n• 回复 \'取消\' 或 /cancel 取消',
        'en': 'Confirm sending?\n• Reply \'confirm\' to send\n• Reply \'cancel\' or /cancel to abort',
    },
    'broadcast_sending': {
        'zh': '⏳ 正在发送广播消息...',
        'en': '⏳ Sending broadcast...',
    },
    'broadcast_complete': {
        'zh': '✅ 广播发送完成！',
        'en': '✅ Broadcast sent!',
    },
    'broadcast_stats': {
        'zh': '📊 发送统计：',
        'en': '📊 Statistics:',
    },
    'broadcast_success': {
        'zh': '成功',
        'en': 'Success',
    },
    'broadcast_failed': {
        'zh': '失败',
        'en': 'Failed',
    },
    
    # 其他
    'cancel_operation': {
        'zh': '❌ 操作已取消',
        'en': '❌ Operation cancelled',
    },
    'please_use_help': {
        'zh': '请使用 /help 查看可用功能。',
        'en': 'Please use /help to see available features.',
    },
}


def get_text(key: str, lang: str = 'zh', **kwargs) -> str:
    """
    获取翻译文本
    
    Args:
        key: 翻译键
        lang: 语言代码 (zh/en)
        **kwargs: 格式化参数
    
    Returns:
        翻译后的文本
    """
    if key not in TRANSLATIONS:
        return key
    
    translation = TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get('zh', key))
    
    # 如果有格式化参数，进行格式化
    if kwargs:
        try:
            translation = translation.format(**kwargs)
        except:
            pass
    
    return translation


