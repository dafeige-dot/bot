"""
FastAPI 应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.api.routes import router


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    app = FastAPI(
        title="Telegram Bot API",
        description="Telegram Bot 定向广播 HTTP API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(router)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("FastAPI 应用启动")
        logger.info(f"API文档: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("FastAPI 应用关闭")
    
    return app


# 创建应用实例
app = create_app()
