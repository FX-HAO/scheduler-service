from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator

# 定义有效的HTTP方法
VALID_HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']


class RequestTaskCreate(BaseModel):
    """请求任务创建模型"""
    name: str
    start_time: float
    header: Optional[dict] = None  # HTTP请求头字段
    method: Optional[Literal['GET', 'POST', 'PUT', 'DELETE',
                             'PATCH', 'HEAD', 'OPTIONS']] = 'GET'  # HTTP请求方法
    request_url: str
    callback_url: Optional[str] = None
    callback_token: Optional[str] = None  # 用于callback_url登录的token
    body: Optional[dict] = None  # HTTP请求体
    cron: Optional[str] = None # cron 表达式

    @field_validator('method')
    @classmethod
    def validate_method(cls, v):
        if v and v.upper() not in VALID_HTTP_METHODS:
            raise ValueError(f"Invalid HTTP method: {v}. Must be one of {VALID_HTTP_METHODS}")
        return v.upper()


class RequestTaskResponse(BaseModel):
    """请求任务响应模型"""
    id: int
    name: str
    user_id: int
    start_time: datetime
    request_url: str
    callback_url: Optional[str]
    callback_token: Optional[str] = None  # 用于callback_url登录的token
    header: Optional[dict] = None  # HTTP请求头字段
    method: str = 'GET'  # HTTP请求方法
    body: Optional[dict] = None  # HTTP请求体
    cron: Optional[str] = None # cron 表达式
    cron_count: int = 0 # cron 任务已经循环的次数
    job_id: Optional[str] = None # APScheduler Job ID
    status: str = "PENDING"
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
