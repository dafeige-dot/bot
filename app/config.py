"""
配置管理模块
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """应用配置"""
    
    # ===== 基础配置 =====
    APP_NAME: str = Field(default="商户管理机器人", env="APP_NAME")
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # ===== Telegram Bot配置 =====
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_BOT_USERNAME: Optional[str] = Field(default=None, env="TELEGRAM_BOT_USERNAME")
    BOT_MODE: str = Field(default="polling", env="BOT_MODE")  # polling 或 webhook
    
    # Webhook配置
    WEBHOOK_URL: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    WEBHOOK_PORT: int = Field(default=8443, env="WEBHOOK_PORT")
    
    # ===== 数据库配置 =====
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://merchant_user:merchant_password@localhost:5432/merchant_bot_db",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    # ===== Redis配置 =====
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # ===== Celery配置 =====
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # ===== OCR配置 =====
    OCR_ENGINE: str = Field(default="paddleocr", env="OCR_ENGINE")
    PADDLEOCR_USE_GPU: bool = Field(default=False, env="PADDLEOCR_USE_GPU")
    PADDLEOCR_LANG: str = Field(default="ch", env="PADDLEOCR_LANG")
    
    # 阿里云OCR
    ALIYUN_OCR_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="ALIYUN_OCR_ACCESS_KEY_ID")
    ALIYUN_OCR_ACCESS_KEY_SECRET: Optional[str] = Field(default=None, env="ALIYUN_OCR_ACCESS_KEY_SECRET")
    ALIYUN_OCR_REGION: str = Field(default="cn-shanghai", env="ALIYUN_OCR_REGION")
    
    # 腾讯云OCR
    TENCENT_SECRET_ID: Optional[str] = Field(default=None, env="TENCENT_SECRET_ID")
    TENCENT_SECRET_KEY: Optional[str] = Field(default=None, env="TENCENT_SECRET_KEY")
    TENCENT_OCR_REGION: str = Field(default="ap-guangzhou", env="TENCENT_OCR_REGION")
    
    # 百度OCR
    BAIDU_OCR_APP_ID: Optional[str] = Field(default=None, env="BAIDU_OCR_APP_ID")
    BAIDU_OCR_API_KEY: Optional[str] = Field(default=None, env="BAIDU_OCR_API_KEY")
    BAIDU_OCR_SECRET_KEY: Optional[str] = Field(default=None, env="BAIDU_OCR_SECRET_KEY")
    
    # ===== 管理员配置 =====
    ADMIN_USER_IDS: str = Field(default="", env="ADMIN_USER_IDS")  # 改为字符串类型
    SUPER_ADMIN_ID: Optional[int] = Field(default=None, env="SUPER_ADMIN_ID")
    
    def get_admin_ids(self) -> List[int]:
        """获取管理员ID列表"""
        if not self.ADMIN_USER_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_USER_IDS.split(",") if id.strip()]
    
    # ===== API配置 =====
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    
    # ===== 安全配置 =====
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = Field(default=1440, env="JWT_EXPIRE_MINUTES")
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")
    
    # ===== 日志配置 =====
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE_PATH: str = Field(default="logs/app.log", env="LOG_FILE_PATH")
    LOG_ROTATION: str = Field(default="100 MB", env="LOG_ROTATION")
    LOG_RETENTION: str = Field(default="30 days", env="LOG_RETENTION")
    
    # ===== 业务配置 =====
    MERCHANT_CODE_EXPIRE_MINUTES: int = Field(default=30, env="MERCHANT_CODE_EXPIRE_MINUTES")
    BALANCE_CACHE_TTL: int = Field(default=60, env="BALANCE_CACHE_TTL")
    MAX_IMAGE_SIZE_MB: int = Field(default=10, env="MAX_IMAGE_SIZE_MB")
    MAX_ORDER_RESULTS: int = Field(default=10, env="MAX_ORDER_RESULTS")
    BROADCAST_DELAY_MS: int = Field(default=100, env="BROADCAST_DELAY_MS")
    
    # ===== 限流配置 =====
    RATE_LIMIT_PER_USER: int = Field(default=20, env="RATE_LIMIT_PER_USER")
    OCR_RATE_LIMIT_PER_HOUR: int = Field(default=50, env="OCR_RATE_LIMIT_PER_HOUR")
    
    # ===== 第三方服务 =====
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = Field(default=False, env="PROMETHEUS_ENABLED")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # ===== 文件存储配置 =====
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    TEMP_DIR: str = Field(default="temp", env="TEMP_DIR")
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")
    
    # 阿里云OSS
    OSS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="OSS_ACCESS_KEY_ID")
    OSS_ACCESS_KEY_SECRET: Optional[str] = Field(default=None, env="OSS_ACCESS_KEY_SECRET")
    OSS_BUCKET_NAME: Optional[str] = Field(default=None, env="OSS_BUCKET_NAME")
    OSS_ENDPOINT: Optional[str] = Field(default=None, env="OSS_ENDPOINT")
    
    # ===== 功能开关 =====
    ENABLE_OCR: bool = Field(default=True, env="ENABLE_OCR")
    ENABLE_BALANCE_QUERY: bool = Field(default=True, env="ENABLE_BALANCE_QUERY")
    ENABLE_BROADCAST: bool = Field(default=True, env="ENABLE_BROADCAST")
    REQUIRE_MERCHANT_AUTH: bool = Field(default=True, env="REQUIRE_MERCHANT_AUTH")
    
    # ===== 数据库备份配置 =====
    BACKUP_ENABLED: bool = Field(default=True, env="BACKUP_ENABLED")
    BACKUP_SCHEDULE: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    BACKUP_PATH: str = Field(default="backups/", env="BACKUP_PATH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def is_admin(self, user_id: int) -> bool:
        """检查用户是否为管理员"""
        return user_id in self.get_admin_ids() or user_id == self.SUPER_ADMIN_ID
    
    def is_super_admin(self, user_id: int) -> bool:
        """检查用户是否为超级管理员"""
        return user_id == self.SUPER_ADMIN_ID


# 创建全局配置实例
settings = Settings()

