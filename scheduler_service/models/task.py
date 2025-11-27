from tortoise import fields
from tortoise.models import Model

from scheduler_service.constants import TaskStatus

# 定义有效的HTTP方法列表
VALID_HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']


class RequestTask(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)
    start_time = fields.DatetimeField(auto_now_add=True)
    request_url = fields.CharField(max_length=128)
    callback_url = fields.CharField(max_length=128, null=True)
    callback_token = fields.CharField(max_length=64, null=True)  # 用于callback_url登录的token
    header = fields.JSONField(null=True)  # HTTP请求头字段
    method = fields.CharField(max_length=10, default='GET')  # HTTP请求方法
    body = fields.JSONField(default=dict)
    message_id = fields.CharField(max_length=64, null=True)  # Dramatiq 消息 ID
    cron = fields.CharField(max_length=64, null=True) # cron 表达式
    cron_count = fields.IntField(default=0) # cron 任务已经循环的次数
    job_id = fields.CharField(max_length=64, null=True)  # APScheduler Job ID
    status = fields.CharField(max_length=20, default=TaskStatus.PENDING)
    error_message = fields.TextField(null=True) # 任务执行失败时的错误信息

    # 定义与User的外键关系
    user = fields.ForeignKeyField(
        'models.User', related_name='request_tasks', source_field='user_id')
    user_id: int

    async def save(self, *args, **kwargs):
        # 验证method是否是有效的HTTP方法
        if self.method and self.method.upper() not in VALID_HTTP_METHODS:
            raise ValueError(
                f"Invalid HTTP method: {self.method}. Must be one of {VALID_HTTP_METHODS}")
        # 保存前转换为大写
        self.method = self.method.upper()
        await super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time,
            "user_id": self.user_id,
            "request_url": self.request_url,
            "callback_url": self.callback_url,
            "callback_token": self.callback_token,
            "header": self.header,
            "method": self.method,
            "body": self.body,
            "message_id": self.message_id,
            "cron": self.cron,
            "cron_count": self.cron_count,
            "job_id": self.job_id,
            "status": self.status,
            "error_message": self.error_message
        }
