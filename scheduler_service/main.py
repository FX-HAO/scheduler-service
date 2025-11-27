"""FastAPI主应用文件"""
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist, IntegrityError

from scheduler_service import close_dramatiq, close_tortoise, setup_dramatiq, get_scheduler
from scheduler_service.api import setup_routes
from scheduler_service.config import Config


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 启动时执行
    await setup_dbs(app)
    
    # 启动调度器
    scheduler = get_scheduler()
    scheduler.start()
    
    # Dramatiq will be set up by the app fixture in tests or via external config in production
    yield
    
    # 关闭调度器
    if scheduler.running:
        scheduler.shutdown()

    # 关闭时执行
    await close_dbs()


def create_app(config: Any = None) -> FastAPI:
    """创建FastAPI应用"""
    # 获取默认配置（Config.to_dict() 会自动加载 TOML 配置）
    default_config = Config.to_dict()

    # 如果传入了配置，则用传入的配置更新默认配置
    if config:
        # 如果传入的是类，获取其字典形式
        if hasattr(config, 'to_dict'):
            config_dict = config.to_dict()
        elif isinstance(config, dict):
            config_dict = config
        else:
            # 尝试将其转换为字典
            config_dict = dict(config.__dict__)

        # 更新默认配置
        default_config.update(config_dict)

    # 使用新的lifespan事件处理器
    app = FastAPI(
        title="调度服务 API",
        description="任务调度服务的RESTful API",
        version="0.3.0",
        lifespan=lifespan  # 设置生命周期管理
    )

    # 存储配置到app实例
    app.config = default_config

    # 注册路由
    setup_routes(app)

    # 注册异常处理器
    @app.exception_handler(DoesNotExist)
    async def does_not_exist_exception_handler(request: Request, exc: DoesNotExist):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_exception_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": [{"loc": [], "msg": str(exc), "type": "IntegrityError"}]},
        )

    # 跨域配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


async def setup_dbs(app: FastAPI):
    """初始化所有数据库连接"""

    # 获取数据库URL，支持多种配置键名
    db_url = app.config.get('POSTGRES_URL') or app.config.get('PG_URL') or app.config.get('DB_URL')
    if not db_url:
        raise ValueError("PostgreSQL数据库URL未配置，请设置POSTGRES_URL、PG_URL或DB_URL")

    # PostgreSQL - Tortoise ORM (使用官方实现)
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["scheduler_service.models"]},
    )
    # 生成数据库架构（仅开发环境建议）
    await Tortoise.generate_schemas()

    # 初始化 Dramatiq
    setup_dramatiq(app.config)


async def close_dbs():
    """关闭所有数据库连接"""
    # 关闭Tortoise连接
    await close_tortoise()
    # 关闭Dramatiq连接
    close_dramatiq()
