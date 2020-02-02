from datetime import datetime
import time

import pytest

from scheduler_service.models import Task, URLDetail
from tests.const import task_url


async def test_task(user):
    await Task.objects.create(name="test",
                              start_time=datetime.now(),
                              user_id=user.id,
                              cookies={"test": "test"})
    task = await Task.objects.get(name="test")
    await task.delete()


async def test_http_task(test_cli, headers):
    resp = await test_cli.post(task_url,
                               headers=headers,
                               json={
                                   "name": "test",
                                   "interval": 1000,
                                   "start_time": time.time()
                               })
    assert resp.status == 200

    resp = await test_cli.get(task_url, headers=headers)
    assert resp.status == 200
    