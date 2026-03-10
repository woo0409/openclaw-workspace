"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from core.config import settings
from core.database import engine, Base
from core.logger import init_logging, get_logger
from api.routes import router
from services.scheduler import scheduler

# 初始化日志系统
init_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动中...")

    # 创建数据库表
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建/检查完成")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")

    # 启动任务调度器
    try:
        scheduler.start()
        logger.info("✅ 任务调度器已启动")
    except Exception as e:
        logger.error(f"❌ 任务调度器启动失败: {e}")

    yield

    # 关闭时
    logger.info(f"{settings.APP_NAME} 关闭中...")

    # 停止任务调度器
    try:
        scheduler.stop()
        logger.info("✅ 任务调度器已停止")
    except Exception as e:
        logger.error(f"❌ 任务调度器停止失败: {e}")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="数据库 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 自定义异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc)
        }
    )


# 注册路由
app.include_router(router, prefix=settings.API_PREFIX)


# 根路径
@app.get("/")
async def root():
    """
    根路径
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": settings.API_PREFIX
    }


# 健康检查
@app.get("/health")
async def health():
    """
    健康检查（无需数据库）
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG
    )
