"""
日志配置模块
"""
import sys
from pathlib import Path
from loguru import logger

from app.config import settings


def setup_logger():
    """配置日志"""
    
    # 移除默认的logger
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # 文件输出
    log_path = Path(settings.LOG_FILE_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.LOG_FILE_PATH,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        encoding="utf-8",
    )
    
    # 错误日志单独记录
    logger.add(
        log_path.parent / "error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="100 MB",
        retention="60 days",
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )
    
    logger.info("日志系统初始化完成")

