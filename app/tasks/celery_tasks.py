"""
Celery异步任务
"""
from celery import Celery
from celery.schedules import crontab
from loguru import logger

from app.config import settings

# 创建Celery应用
celery_app = Celery(
    "merchant_bot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每天凌晨2点备份数据库
    "backup-database": {
        "task": "app.tasks.celery_tasks.backup_database",
        "schedule": crontab(hour=2, minute=0),
    },
    # 每小时清理临时文件
    "cleanup-temp-files": {
        "task": "app.tasks.celery_tasks.cleanup_temp_files",
        "schedule": crontab(minute=0),
    },
    # 每天统计数据
    "daily-statistics": {
        "task": "app.tasks.celery_tasks.generate_daily_statistics",
        "schedule": crontab(hour=1, minute=0),
    },
}


@celery_app.task(name="app.tasks.celery_tasks.process_ocr_image")
def process_ocr_image(image_path: str, merchant_id: int, order_id: int = None):
    """
    处理OCR图片识别（异步）
    """
    try:
        from app.services.ocr import OCRService
        import asyncio
        
        ocr_service = OCRService()
        
        # 在异步上下文中运行
        result = asyncio.run(ocr_service.recognize_order_image(image_path))
        
        logger.info(f"OCR任务完成: {image_path}")
        
        return result
        
    except Exception as e:
        logger.error(f"OCR任务失败: {e}")
        raise


@celery_app.task(name="app.tasks.celery_tasks.send_broadcast")
def send_broadcast(merchant_ids: list, message: str, parse_mode: str = None):
    """
    发送广播消息（异步）
    """
    try:
        from telegram import Bot
        from app.services.broadcast import BroadcastService
        import asyncio
        
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        broadcast_service = BroadcastService(bot)
        
        # 在异步上下文中运行
        result = asyncio.run(
            broadcast_service.broadcast_to_merchants(
                merchant_ids=merchant_ids,
                message=message,
                parse_mode=parse_mode
            )
        )
        
        logger.info(f"广播任务完成: 成功 {result['success']}/{result['total']}")
        
        return result
        
    except Exception as e:
        logger.error(f"广播任务失败: {e}")
        raise


@celery_app.task(name="app.tasks.celery_tasks.backup_database")
def backup_database():
    """
    备份数据库（定时任务）
    """
    try:
        import subprocess
        from datetime import datetime
        from pathlib import Path
        
        if not settings.BACKUP_ENABLED:
            logger.info("数据库备份未启用")
            return
        
        # 创建备份目录
        backup_dir = Path(settings.BACKUP_PATH)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.sql"
        
        # 执行备份（PostgreSQL）
        # 注意：需要配置PGPASSWORD环境变量
        db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "")
        
        # TODO: 实现实际的数据库备份逻辑
        logger.info(f"数据库备份任务执行: {backup_file}")
        
        # 清理旧备份
        cleanup_old_backups()
        
        return str(backup_file)
        
    except Exception as e:
        logger.error(f"数据库备份失败: {e}")
        raise


@celery_app.task(name="app.tasks.celery_tasks.cleanup_temp_files")
def cleanup_temp_files():
    """
    清理临时文件（定时任务）
    """
    try:
        from pathlib import Path
        import time
        
        temp_dir = Path(settings.TEMP_DIR)
        
        if not temp_dir.exists():
            return
        
        # 删除1小时前的临时文件
        current_time = time.time()
        deleted_count = 0
        
        for file_path in temp_dir.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                
                # 超过1小时的文件删除
                if file_age > 3600:
                    file_path.unlink()
                    deleted_count += 1
        
        logger.info(f"清理临时文件: 删除 {deleted_count} 个文件")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"清理临时文件失败: {e}")
        raise


@celery_app.task(name="app.tasks.celery_tasks.generate_daily_statistics")
def generate_daily_statistics():
    """
    生成每日统计数据（定时任务）
    """
    try:
        from datetime import datetime, timedelta
        import asyncio
        from app.services.order import OrderService
        
        # 计算昨天的日期范围
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取统计数据
        order_service = OrderService()
        stats = asyncio.run(
            order_service.get_order_statistics(
                start_date=start_date,
                end_date=end_date
            )
        )
        
        logger.info(f"每日统计生成完成: {stats}")
        
        # TODO: 保存统计数据到数据库或发送通知
        
        return stats
        
    except Exception as e:
        logger.error(f"生成每日统计失败: {e}")
        raise


def cleanup_old_backups():
    """清理旧备份文件"""
    try:
        from pathlib import Path
        from datetime import datetime, timedelta
        
        backup_dir = Path(settings.BACKUP_PATH)
        
        if not backup_dir.exists():
            return
        
        # 计算保留期限
        retention_date = datetime.now() - timedelta(days=settings.BACKUP_RETENTION_DAYS)
        
        deleted_count = 0
        for backup_file in backup_dir.glob("backup_*.sql*"):
            if backup_file.is_file():
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if file_mtime < retention_date:
                    backup_file.unlink()
                    deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"清理旧备份: 删除 {deleted_count} 个文件")
            
    except Exception as e:
        logger.error(f"清理旧备份失败: {e}")


# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])

