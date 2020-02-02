import asyncio
import databases
import pytest
import sqlalchemy

from scheduler_service.manage import app as sanic_app, pg_db
from scheduler_service.models import metadata, User


@pytest.fixture(scope="session", autouse=True)
def app():
    engine = sqlalchemy.create_engine(str(pg_db.url))
    print("create database")
    metadata.create_all(engine)
    yield sanic_app
    print("drop database")
    metadata.drop_all(engine)


@pytest.fixture
def test_cli(loop: asyncio.AbstractEventLoop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


@pytest.fixture
async def user(test_cli):
    passwd_hash = User.hash_password("password")
    return await User.objects.create(name="test",
                              password_hash=passwd_hash,
                              email="test@test.com",
                              verify=True)
@pytest.fixture
def token(app, user: User,):
    return user.generate_auth_token(app)


@pytest.fixture
def headers(token):
    return {"Authorization": token}