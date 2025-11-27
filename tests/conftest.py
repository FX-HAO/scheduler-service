import os
import dramatiq # Import for debugging

import pytest
from dramatiq import Worker
from httpx import AsyncClient

# 必须在导入任何 scheduler_service 模块之前设置此环境变量
os.environ["UNIT_TESTS"] = "1"

from scheduler_service import close_dramatiq, setup_dramatiq, scheduler  # noqa: E402
from scheduler_service.main import (close_dbs, create_app,  # noqa: E402
                                    setup_dbs)
from scheduler_service.models import User  # noqa: E402


@pytest.fixture
async def client(app):
    """获取测试客户端"""
    # 注意：这里不使用上下文管理器触发lifespan，因为我们已经手动管理了数据库生命周期
    # 这样可以避免lifespan和手动初始化冲突
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def stub_broker():
    """使用内存broker进行Dramatiq测试"""
    # 现在 broker.py 会因为 UNIT_TESTS=1 返回 StubBroker
    from scheduler_service import broker
    
    print(f"\n[DEBUG] conftest.stub_broker fixture called")
    print(f"[DEBUG] Imported 'broker' from scheduler_service: {broker}")
    print(f"[DEBUG] dramatiq.get_broker() returns: {dramatiq.get_broker()}")
    
    broker.flush_all()
    return broker


@pytest.fixture
def stub_worker(stub_broker):
    """使用内存worker进行Dramatiq测试"""
    worker = Worker(stub_broker, worker_timeout=100)
    worker.start()
    yield worker
    worker.stop()


@pytest.fixture
async def app():
    """创建并启动测试应用"""
    # 使用测试数据库URL
    # 使用文件数据库以确保连接共享
    db_url = "sqlite://test.db"

    # 清理旧的测试数据库及相关文件
    if os.path.exists("test.db"):
        os.remove("test.db")
    if os.path.exists("test.db-shm"):
        os.remove("test.db-shm")
    if os.path.exists("test.db-wal"):
        os.remove("test.db-wal")

    test_config = {
        "POSTGRES_URL": db_url,
        "SECRET_KEY": "test-secret-key",
        # 显式禁用 RabbitMQ 连接，防止 setup_dramatiq 尝试连接
        "DRAMATIQ_URL": None
    }

    app = create_app(test_config)

    # 手动初始化数据库，确保在测试开始前数据库已就绪
    await setup_dbs(app)

    # Dramatiq setup - this initializes the global scheduler variable
    setup_dramatiq(app.config)

    # Start the APScheduler instance for tests
    if scheduler and not scheduler.running:
        scheduler.start()

    yield app

    # Shut down APScheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False) # Faster shutdown for tests

    # 关闭数据库连接
    await close_dbs()

    # 关闭Dramatiq连接
    close_dramatiq() # This handles Dramatiq broker shutdown

    # 清理所有测试数据库文件
    if os.path.exists("test.db"):
        os.remove("test.db")
    if os.path.exists("test.db-shm"):
        os.remove("test.db-shm")
    if os.path.exists("test.db-wal"):
        os.remove("test.db-wal")


@pytest.fixture
async def user(app): # 依赖app确保DB已初始化
    """创建测试用户"""
    password_hash = User.hash_password("password")
    user = await User.create(
        name="test",
        password_hash=password_hash,
        email="test@test.com",
        verify=True
    )
    return user


@pytest.fixture
async def token(app, user: User):
    """获取测试用户的认证令牌"""
    return user.generate_auth_token(app.config["SECRET_KEY"])


@pytest.fixture
async def headers(token):
    """创建带有认证头的请求头"""
    return {"Authorization": f"Bearer {token}"}
