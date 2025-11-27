"""API模块初始化"""
from fastapi import APIRouter

from scheduler_service.api.v1 import task, user


def setup_routes(app):
    """设置路由"""
    # 创建API路由器
    api_router = APIRouter()

    # 注册v1版本路由
    api_router.include_router(task.router, prefix="/tasks", tags=["tasks"])
    api_router.include_router(user.router, prefix="/users", tags=["users"])

    # 将API路由器注册到应用
    app.include_router(api_router, prefix="/api/v1")
