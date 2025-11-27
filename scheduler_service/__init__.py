import os
import urllib.parse
import dramatiq
import redis
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
from dramatiq.middleware import AsyncIO
from dramatiq_abort import Abortable
from dramatiq_abort.backends.redis import RedisBackend
from tortoise import Tortoise
from tortoise.exceptions import ConfigurationError

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from scheduler_service.utils.logger import logger
from scheduler_service.config import Config


# --- Helper Functions ---
def _get_redis_job_store(redis_url: str) -> RedisJobStore:
    """
    Parses a Redis URL and returns a configured RedisJobStore.
    Handles redis://[:password@]host[:port][/db] format.
    """
    try:
        url_parts = urllib.parse.urlparse(redis_url)

        return RedisJobStore(
            jobs_key='apscheduler.jobs',
            run_times_key='apscheduler.run_times',
            host=url_parts.hostname or 'localhost',
            port=url_parts.port or 6379,
            db=int(url_parts.path.lstrip('/')) if url_parts.path else 0,
            password=url_parts.password
        )
    except Exception:
        return RedisJobStore(host='localhost', port=6379)


def generate_broker(config):
    """
    根据配置生成并返回一个配置好的 Dramatiq Broker 实例。
    支持测试模式 (UNIT_TESTS=1) 使用 StubBroker。
    """
    if os.getenv("UNIT_TESTS") == "1":
        # [Test Mode]
        # Use StubBroker for in-memory testing
        broker = StubBroker()
        broker.emit_after("process_boot")
        # Add AsyncIO middleware (needed for async actors)
        broker.add_middleware(AsyncIO())
        # Test mode typically doesn't need Abortable unless mocking backend
        return broker
    else:
        # [Production Mode]
        # Config.REDIS_URL is populated from env vars or config file
        # Note: `config` here can be the Config class or a dict/object with .REDIS_URL or .get("REDIS_URL")
        # We handle both for robustness
        redis_url = getattr(config, "REDIS_URL", None) or (config.get("REDIS_URL") if isinstance(config, dict) else None)

        if not redis_url:
            # Fallback or error
            redis_url = "redis://localhost:6379/0"

        broker = RedisBroker(url=redis_url)

        # Add Middleware
        broker.add_middleware(AsyncIO())

        # Abortable Middleware
        try:
            redis_client = redis.Redis.from_url(redis_url)
            abort_backend = RedisBackend(client=redis_client)
            broker.add_middleware(Abortable(backend=abort_backend))
        except Exception as e:
            logger.warning("Failed to configure Abortable middleware: %s", e)

        return broker


# --- Global Initialization ---
# Initialize the global broker using the default Config immediately on import.
# This ensures that any actors defined in other modules will register against this broker.
broker = generate_broker(Config)
dramatiq.set_broker(broker)

# Global scheduler instance (placeholder, fully configured in setup_dramatiq or via default logic)
scheduler: AsyncIOScheduler = None


def get_scheduler() -> AsyncIOScheduler:
    """获取APScheduler实例，如果未初始化则抛出错误"""
    global scheduler
    if scheduler is None:
        raise RuntimeError("APScheduler has not been initialized. Call setup_dramatiq first.")
    return scheduler


# --- Setup Functions ---
def setup_dramatiq(config):
    """
    初始化Dramatiq消息队列和APScheduler（不启动）。
    启动和关闭由应用的生命周期或测试夹具管理。
    """
    global scheduler, broker

    if os.getenv("UNIT_TESTS") == "1":
        # --- [测试模式] ---
        jobstores = {'default': MemoryJobStore()}
        scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Asia/Shanghai")

    else:
        # --- [生产模式] ---
        current_broker = generate_broker(config)
        dramatiq.set_broker(current_broker)
        broker = current_broker # 更新模块级变量

        redis_url = config.get("REDIS_URL")
        if redis_url:
            jobstores = {'default': _get_redis_job_store(redis_url)}
            scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Asia/Shanghai")
        else:
            scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


def close_dramatiq():
    """关闭Dramatiq连接"""
    current_broker = dramatiq.get_broker()
    if current_broker:
        current_broker.close()

    # Shut down APScheduler (only if it was started and is running)
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()


async def setup_tortoise(config):
    """初始化Tortoise-ORM"""
    db_url = config.get('PG_URL') or config.get('POSTGRES_URL') or config.get('DB_URL')
    if not db_url:
        raise ValueError("数据库URL未配置，请设置PG_URL、POSTGRES_URL或DB_URL环境变量")

    await Tortoise.init(
        db_url=db_url,
        modules={'models': ['scheduler_service.models']}
    )


async def close_tortoise():
    """关闭Tortoise连接，不依赖Sanic应用"""
    try:
        await Tortoise.close_connections()
    except ConfigurationError:
        # 如果未初始化，忽略错误
        pass
