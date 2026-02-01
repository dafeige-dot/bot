"""
API 服务器启动脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from loguru import logger

from app.config import settings
from app.utils.logger import setup_logger


def main():
    """启动API服务器"""
    
    # 设置日志
    setup_logger()
    
    logger.info("=" * 50)
    logger.info("Telegram Bot API Server")
    logger.info(f"环境: {settings.APP_ENV}")
    logger.info(f"监听: {settings.API_HOST}:{settings.API_PORT}")
    logger.info("=" * 50)
    
    # 启动uvicorn
    uvicorn.run(
        "app.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.APP_ENV == "development",
        log_level="info"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出...")
    except Exception as e:
        logger.exception(f"程序异常退出: {e}")
        sys.exit(1)
