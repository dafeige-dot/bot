"""
Telegram Bot 主入口文件
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from app.config import settings
from app.bot import handlers, commands, callbacks
from app.utils.logger import setup_logger
from app.database.session import init_db


async def post_init_commands(application: Application) -> None:
    """设置Bot命令菜单"""
    logger.info("Bot初始化完成，开始运行...")
    
    # 设置Bot命令菜单（中文）
    await application.bot.set_my_commands([
        ("language", "切换语言 / Change Language"),
        ("balance", "余额 / Balance"),
        ("order", "订单 / Order"),
        ("help", "帮助 / Help"),
    ])
    
    # 如果是管理员，添加管理命令
    admin_ids = settings.get_admin_ids()
    if admin_ids:
        logger.info(f"管理员ID: {admin_ids}")


async def post_shutdown(application: Application) -> None:
    """关闭前的回调"""
    logger.info("Bot正在关闭...")


def setup_handlers(application: Application) -> None:
    """设置消息处理器"""
    
    # 命令处理器
    application.add_handler(CommandHandler("help", commands.help_command))
    application.add_handler(CommandHandler("myid", commands.myid_command))
    application.add_handler(CommandHandler("balance", commands.balance_command))
    # 余额查询别名
    application.add_handler(CommandHandler("ye", commands.balance_command))
    application.add_handler(CommandHandler("query", commands.balance_command))
    application.add_handler(CommandHandler("order", commands.order_command))
    # UPI 连通性测试命令（不在菜单中）
    application.add_handler(CommandHandler("upi", commands.upi_command))
    # 补单命令
    application.add_handler(CommandHandler("bd", commands.bd_command))
    # 订单查询别名
    application.add_handler(CommandHandler("cd", commands.order_command))
    application.add_handler(CommandHandler("zd", commands.order_command))
    application.add_handler(CommandHandler("history", commands.history_command))
    application.add_handler(CommandHandler("upload", commands.upload_command))
    application.add_handler(CommandHandler("cancel", commands.cancel_command))
    application.add_handler(CommandHandler("reset", commands.reset_command))
    
    # 语言切换
    from app.bot.language import language_command
    application.add_handler(CommandHandler("language", language_command))
    
    # 管理员命令
    application.add_handler(CommandHandler("bind", commands.bind_command))
    application.add_handler(CommandHandler("broadcast", commands.broadcast_command))
    # 广播别名
    application.add_handler(CommandHandler("gb", commands.broadcast_command))
    application.add_handler(CommandHandler("broadcast_channel", commands.broadcast_channel_command))
    # 频道广播别名
    application.add_handler(CommandHandler("gbc", commands.broadcast_channel_command))
    application.add_handler(CommandHandler("get_chat_id", commands.get_chat_id_command))
    # 获取聊天ID别名
    application.add_handler(CommandHandler("chatid", commands.get_chat_id_command))
    application.add_handler(CommandHandler("stats", commands.stats_command))
    application.add_handler(CommandHandler("merchants", commands.merchants_command))
    application.add_handler(CommandHandler("toggle_ocr", commands.toggle_ocr_command))
    
    # 回调查询处理器
    application.add_handler(CallbackQueryHandler(callbacks.button_callback))
    
    # 图片处理器
    application.add_handler(
        MessageHandler(filters.PHOTO, handlers.photo_handler)
    )
    
    # 文本消息处理器
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_handler)
    )
    
    # 错误处理器
    application.add_error_handler(handlers.error_handler)
    
    logger.info("所有处理器已注册")


async def init_and_run(application: Application):
    """初始化并运行Bot"""
    # 初始化数据库
    logger.info("正在初始化数据库...")
    try:
        await init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    
    # 设置命令
    await post_init_commands(application)


def main() -> None:
    """主函数"""
    
    # 设置日志
    setup_logger()
    
    logger.info(f"=" * 50)
    logger.info(f"{settings.APP_NAME} v{__import__('app').__version__}")
    logger.info(f"环境: {settings.APP_ENV}")
    logger.info(f"运行模式: {settings.BOT_MODE}")
    logger.info(f"=" * 50)
    
    # 创建必要的目录
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # 创建Bot应用
    logger.info("正在创建Bot应用...")
    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(init_and_run)  # 在这里初始化数据库
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # 设置处理器
    setup_handlers(application)
    
    # 启动Bot
    if settings.BOT_MODE == "webhook":
        if not settings.WEBHOOK_URL:
            logger.error("Webhook模式需要配置WEBHOOK_URL")
            sys.exit(1)
        
        logger.info(f"使用Webhook模式: {settings.WEBHOOK_URL}")
        application.run_webhook(
            listen="0.0.0.0",
            port=settings.WEBHOOK_PORT,
            url_path=settings.TELEGRAM_BOT_TOKEN,
            webhook_url=f"{settings.WEBHOOK_URL}/{settings.TELEGRAM_BOT_TOKEN}",
        )
    else:
        logger.info("使用Polling模式")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出...")
    except Exception as e:
        logger.exception(f"程序异常退出: {e}")
        sys.exit(1)

