import dramatiq
import httpx
from tortoise.expressions import F

from scheduler_service.constants import RequestStatus, TaskStatus
from scheduler_service.models import RequestTask
from scheduler_service.utils.logger import logger

# 定义全局session
_session = None


def get_session():
    """获取httpx会话"""
    global _session
    if _session is None or _session.is_closed:
        _session = httpx.AsyncClient(timeout=60.0)
    return _session


async def close_session():
    """关闭httpx会话"""
    global _session
    if _session and not _session.is_closed:
        await _session.aclose()


async def trigger_cron_task(task_id):
    """
    由APScheduler调用的任务触发器。
    发送任务到Dramatiq并更新循环计数。
    """
    # 发送任务到消息队列
    ping.send(task_id)

    # 更新循环计数
    # 使用F表达式进行原子更新
    await RequestTask.filter(id=task_id).update(cron_count=F('cron_count') + 1)


@dramatiq.actor
async def ping(task_id):
    """执行ping任务"""
    session = get_session()
    callback_data = None

    # 从数据库获取任务信息
    task = await RequestTask.get_or_none(id=task_id)
    if not task:
        logger.warning("Task with id %s not found", task_id)
        return

    # 更新状态为运行中，并清除之前的错误信息
    task.status = TaskStatus.RUNNING
    task.error_message = None
    await task.save()

    try:
        # 准备基础请求参数
        request_kwargs = {
            'url': task.request_url,
            'headers': task.header if task.header else {}
        }

        # 如果有body，作为请求体
        if task.body:
            request_kwargs['json'] = task.body

        # 根据method执行相应的HTTP请求（已在保存时转换为大写）
        match task.method:
            case 'POST':
                response = await session.post(**request_kwargs)
            case 'PUT':
                response = await session.put(**request_kwargs)
            case 'DELETE':
                response = await session.delete(**request_kwargs)
            case 'PATCH':
                response = await session.patch(**request_kwargs)
            case _:
                # 默认使用GET（包括当method为GET或其他未知方法时）
                response = await session.get(**request_kwargs)

        # 读取响应内容
        content = await response.aread()
        callback_data = {
            'response': content.decode('utf-8'),
            'code': response.status_code,
            'exception': None,
            'status': RequestStatus.COMPLETE
        }

        # 更新状态为完成
        task.status = TaskStatus.COMPLETED
        await task.save()

    except Exception as e:
        # 处理请求异常
        logger.error("Error requesting task %s: %s", task_id, e)
        callback_data = {
            'response': None,
            'code': None,
            'exception': str(e),
            'status': RequestStatus.FAIL
        }
        # 更新状态为失败，并记录错误信息
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        await task.save()

    # 发送回调（无论请求成功与否，只要有回调URL和回调数据）
    if task.callback_url and callback_data:
        try:
            await session.post(
                task.callback_url,
                json=callback_data
            )
        except Exception as e:
            logger.error("Error sending callback to %s: %s", task.callback_url, e)


# 注册启动和关闭钩子
@dramatiq.actor
async def startup_worker():
    """worker启动时执行"""
    global _session
    _session = httpx.AsyncClient(timeout=60.0)


@dramatiq.actor
async def shutdown_worker():
    """worker关闭时执行"""
    await close_session()
