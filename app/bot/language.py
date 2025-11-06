"""
语言相关命令处理
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from app.i18n import get_text, set_language
from app.services.merchant import MerchantService


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /language 命令"""
    user = update.effective_user
    
    # 获取当前语言
    merchant_service = MerchantService()
    merchant = await merchant_service.get_by_telegram_id(user.id)
    
    current_lang = merchant.language if merchant else 'zh'
    
    # 创建语言选择键盘
    keyboard = [
        [
            InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh"),
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text('language_select', lang=current_lang),
        reply_markup=reply_markup
    )


async def language_callback(query, user_id: int, lang_code: str):
    """处理语言切换回调"""
    try:
        # 更新用户语言偏好
        merchant_service = MerchantService()
        merchant = await merchant_service.get_by_telegram_id(user_id)
        
        if merchant:
            await merchant_service.update_merchant(
                merchant.id,
                language=lang_code
            )
        
        # 更新内存中的语言设置
        set_language(user_id, lang_code)
        
        # 发送确认消息
        await query.edit_message_text(
            get_text('language_changed', lang=lang_code)
        )
        
        logger.info(f"用户 {user_id} 切换语言到 {lang_code}")
        
    except Exception as e:
        logger.error(f"切换语言失败: {e}")
        await query.edit_message_text(
            "❌ Language change failed / 语言切换失败"
        )


