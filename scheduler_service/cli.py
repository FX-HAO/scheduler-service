import logging
import sys
import asyncio

import click
from aerich import Command
from tortoise import Tortoise

from scheduler_service import close_tortoise, setup_tortoise
from scheduler_service.main import create_app
from scheduler_service.config import Config, TORTOISE_ORM
from scheduler_service.models import User


@click.group()
def scheduler():
    """Scheduler Service 命令行工具"""
    click.echo("Scheduler Service CLI")


@scheduler.command()
def shell():
    """启动交互式shell"""
    from IPython import embed
    app = create_app()
    context = {
        "app": app,
        "User": User
    }
    embed(user_ns=context,
          colors="neutral",
          using="asyncio",
          header="First: await app._database.connect()")


@scheduler.command()
@click.option('-h', "--host", default="localhost")
@click.option('-p', "--port", default=8080, type=int)
@click.option('-w', "--workers", default=1, type=int)
@click.option('--debug/--no-debug', default=True)
@click.option('--access-log/--no-access-log', default=True)
def runserver(host, port, workers, debug, access_log):
    """启动Web服务器（开发环境使用）"""
    import uvicorn

    # 使用字符串导入路径，以支持热重载功能
    # create_app函数内部会自动调用Config.to_dict()获取配置
    uvicorn.run(
        "scheduler_service.main:create_app",
        host=host,
        port=port,
        reload=debug,  # 开发模式下启用热重载
        access_log=access_log,
        factory=True  # 告知uvicorn这是一个应用工厂函数
    )


@scheduler.command()
@click.option('-v', '--verbose', is_flag=True, help='启用详细输出')
@click.option('-p', '--processes', default=1, type=int, help='worker进程数量')
def worker(verbose, processes):
    """启动dramatiq worker"""
    # 配置日志
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # 确保应用已初始化 (加载配置和注册任务)
    _ = create_app()

    # 运行dramatiq worker
    from dramatiq.cli import main

    # 保存原始argv，避免修改全局状态
    original_argv = sys.argv.copy()
    try:
        sys.argv = [sys.argv[0], 'scheduler_service.service', '--processes', str(processes)]
        main()
    except KeyboardInterrupt:
        print("Worker stopped")
    finally:
        sys.argv = original_argv


@scheduler.command()
def init_db():
    """初始化数据库 (使用 Aerich)"""
    async def run():
        try:
            command = Command(tortoise_config=TORTOISE_ORM, location="./migrations")
            await command.init()
            await command.init_db(safe=True)
            click.echo("数据库初始化完成 (Aerich)")
        except FileExistsError:
             # 如果 migrations 文件夹已存在，init() 会报错，但这通常没问题，继续尝试 init-db
             # 但 Aerich 的 init() 内部如果文件夹存在只是打印信息或报错，取决于版本。
             # 我们这里假设 init() 失败可能是因为已经初始化过，尝试直接 init-db
             pass
        except Exception as e:
            click.echo(f"初始化过程中遇到问题: {e}")
            click.echo("尝试运行 'scheduler migrate init-db' 以获取详细信息或使用不同选项。")

    asyncio.run(run())


@scheduler.group()
def migrate():
    """数据库迁移工具 (Aerich)"""
    pass


@migrate.command()
def init():
    """初始化 Aerich 配置和目录"""
    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, location="./migrations")
        await command.init()
        click.echo("Aerich initialized")
    asyncio.run(run())


@migrate.command()
@click.option("--safe", is_flag=True, default=True, help="Safe mode")
def init_db(safe):
    """初始化数据库 (创建表)"""
    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, location="./migrations")
        await command.init()
        await command.init_db(safe=safe)
        click.echo("Database initialized")
    asyncio.run(run())


@migrate.command()
@click.option("--name", default="update", help="Migration name")
def create(name):
    """创建新的迁移文件"""
    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, location="./migrations")
        await command.init()
        await command.migrate(name)
        click.echo(f"Migration '{name}' created")
    asyncio.run(run())


@migrate.command()
def upgrade():
    """应用迁移"""
    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, location="./migrations")
        await command.init()
        await command.upgrade()
        click.echo("Database upgraded")
    asyncio.run(run())


@migrate.command()
def downgrade():
    """回滚迁移"""
    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, location="./migrations")
        await command.init()
        await command.downgrade(delete=False, version=-1)
        click.echo("Database downgraded")
    asyncio.run(run())


@migrate.command()
def history():
    """查看迁移历史"""
    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, location="./migrations")
        await command.init()
        versions = await command.history()
        for version in versions:
            click.echo(version)
    asyncio.run(run())


@migrate.command()
def heads():
    """查看当前迁移头部"""
    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, location="./migrations")
        await command.init()
        heads = await command.heads()
        for head in heads:
            click.echo(head)
    asyncio.run(run())


@scheduler.command()
@click.option('--path', '-p', help='要测试的路径，默认为tests/')
@click.option('--coverage', '-c', is_flag=True, help='生成覆盖率报告')
@click.option('--verbose', '-v', is_flag=True, help='显示详细输出')
@click.option('--parallel', '-n', type=int, help='并行执行的进程数')
@click.option(
    "--coverage-threshold", "-t",
    type=int,
    default=80,
    help="覆盖率阈值，默认为80%%"
)
def test(path, coverage, verbose, parallel, coverage_threshold):
    """启动覆盖率测试"""
    import subprocess

    # 构建pytest命令
    cmd = [sys.executable, "-m", "pytest"]

    # 添加测试路径
    if path:
        cmd.append(path)
    else:
        cmd.append("tests/")

    # 添加覆盖率选项
    if coverage:
        cmd.extend([
            "--cov=scheduler_service",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml"
        ])

        # 添加覆盖率阈值
        if coverage_threshold:
            cmd.append(f"--cov-fail-under={coverage_threshold}")

    # 添加详细输出
    if verbose:
        cmd.append("-v")

    # 添加并行执行
    if parallel:
        cmd.append(f"-n={parallel}")

    click.echo(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    # 如果生成了HTML覆盖率报告，显示路径
    if coverage and result.returncode == 0:
        click.echo("\nHTML coverage report generated in htmlcov/index.html")

    sys.exit(result.returncode)


if __name__ == '__main__':
    scheduler()
