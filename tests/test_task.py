import time
from datetime import datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from scheduler_service.constants import RequestStatus, TaskStatus
from scheduler_service.models import RequestTask
from tests import const


@pytest.mark.asyncio
class TestTaskModel:
    """测试RequestTask模型"""

    async def test_create_task(self, user):
        """测试创建任务"""
        task = await RequestTask.create(
            name="test_task",
            start_time=datetime.now(),
            user_id=user.id,
            request_url="http://example.com",
            callback_url="http://example.com/callback",
            method="GET"
        )
        assert task.name == "test_task"
        assert task.user_id == user.id
        assert task.method == "GET"
        await task.delete()

    async def test_task_method_validation(self, user):
        """测试HTTP方法验证"""
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
            task = await RequestTask.create(
                name=f"test_{method.lower()}",
                start_time=datetime.now(),
                user_id=user.id,
                request_url="http://example.com",
                callback_url="http://example.com/callback",
                method=method
            )
            assert task.method == method.upper()
            await task.delete()

        with pytest.raises(ValueError, match="Invalid HTTP method"):
            await RequestTask.create(
                name="invalid_method",
                start_time=datetime.now(),
                user_id=user.id,
                request_url="http://example.com",
                method="INVALID"
            )

    async def test_task_to_dict(self, user):
        """测试任务转字典方法"""
        task = await RequestTask.create(
            name="dict_test",
            start_time=datetime.now(),
            user_id=user.id,
            request_url="http://example.com",
            callback_url="http://example.com/callback",
            method="POST",
            header={"Authorization": "Bearer token"},
            body={"data": "test"}
        )
        task_dict = task.to_dict()
        assert task_dict["name"] == "dict_test"
        assert task_dict["method"] == "POST"
        assert task_dict["header"] == {"Authorization": "Bearer token"}
        assert task_dict["body"] == {"data": "test"}
        await task.delete()


@pytest.mark.asyncio
class TestTaskAPI:
    """测试任务API端点"""

    async def test_create_task_api(self, client, headers, mocker):
        """测试创建任务API，并模拟网络请求"""
        mock_response = mocker.AsyncMock()
        mock_response.status_code = 200
        mock_response.aread.return_value = b"ok"

        mock_client = mocker.AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.get.return_value = mock_response

        mocker.patch("scheduler_service.service.request.get_session", return_value=mock_client)

        task_data = {
            "name": "api_test_task",
            "start_time": time.time(),
            "request_url": "http://example.com",
            "callback_url": "http://example.com/callback",
            "method": "POST",
            "header": {"Content-Type": "application/json"},
            "body": {"key": "value"}
        }

        resp = await client.post(const.TASK_URL, headers=headers, json=task_data)
        assert resp.status_code == 200
        response_data = resp.json()
        assert "task_id" in response_data

        # 验证任务被放入队列
        # 由于没有启动 worker，任务应该留在队列中
        from scheduler_service import broker
        assert broker.queues["default"].qsize() == 1

        task_id = response_data["task_id"]
        await client.delete(f"{const.TASK_URL}/{task_id}", headers=headers)

    async def test_create_task_delayed(self, client, headers, mocker):
        """测试创建延迟任务"""
        # 模拟当前时间为 T
        current_time = 1000000000.0  # 2001-09-09...
        start_time = current_time + 60  # 60秒后

        mocker.patch("time.time", return_value=current_time)
        
        # Mock ping actor
        mock_ping = mocker.patch("scheduler_service.api.v1.task.ping")
        mock_message = mocker.Mock()
        mock_message.message_id = "msg_123"
        mock_ping.send_with_options.return_value = mock_message
        mock_ping.send.return_value = mock_message
        
        # Case 1: Future start_time -> Delayed execution
        task_data = {
            "name": "delayed_task",
            "start_time": start_time,
            "request_url": "http://example.com",
            "method": "GET"
        }

        resp = await client.post(const.TASK_URL, headers=headers, json=task_data)
        assert resp.status_code == 200
        
        # 验证 send_with_options 被调用，且 eta 正确
        expected_eta = int(start_time * 1000)
        mock_ping.send_with_options.assert_called_once()
        call_args = mock_ping.send_with_options.call_args
        assert call_args.kwargs['eta'] == expected_eta
        mock_ping.send.assert_not_called()
        
        # Case 2: Past start_time -> Immediate execution
        mock_ping.reset_mock()
        task_data["start_time"] = current_time - 60 # 过去时间
        task_data["name"] = "immediate_task"
        
        resp = await client.post(const.TASK_URL, headers=headers, json=task_data)
        assert resp.status_code == 200
        
        mock_ping.send.assert_called_once()
        mock_ping.send_with_options.assert_not_called()

    async def test_get_tasks(self, client, headers, user):
        """测试获取任务列表"""
        task1 = await RequestTask.create(
            name="task1",
            start_time=datetime.now(),
            user_id=user.id,
            request_url="http://example.com/1"
        )
        task2 = await RequestTask.create(
            name="task2",
            start_time=datetime.now(),
            user_id=user.id,
            request_url="http://example.com/2"
        )

        resp = await client.get(const.TASK_URL, headers=headers)
        assert resp.status_code == 200
        response_data = resp.json()
        assert "tasks" in response_data
        assert len(response_data["tasks"]) >= 2

        await task1.delete()
        await task2.delete()

    async def test_get_task(self, client, headers, user):
        """测试获取单个任务"""
        task = await RequestTask.create(
            name="single_task",
            start_time=datetime.now(),
            user_id=user.id,
            request_url="http://example.com/single",
            method="POST",
            body={"test": "data"}
        )

        resp = await client.get(f"{const.TASK_URL}/{task.id}", headers=headers)
        assert resp.status_code == 200
        response_data = resp.json()
        assert response_data["name"] == "single_task"
        assert response_data["method"] == "POST"
        assert response_data["body"] == {"test": "data"}

        await task.delete()

    async def test_get_nonexistent_task(self, client, headers):
        """测试获取不存在的任务"""
        resp = await client.get(f"{const.TASK_URL}/99999", headers=headers)
        assert resp.status_code == 404

    async def test_delete_task(self, client, headers, user):
        """测试删除任务"""
        task = await RequestTask.create(
            name="delete_me",
            start_time=datetime.now(),
            user_id=user.id,
            request_url="http://example.com/delete"
        )
        task_id = task.id

        resp = await client.delete(f"{const.TASK_URL}/{task_id}", headers=headers)
        assert resp.status_code == 200

        resp = await client.get(f"{const.TASK_URL}/{task_id}", headers=headers)
        assert resp.status_code == 404

    async def test_delete_nonexistent_task(self, client, headers):
        """测试删除不存在的任务"""
        resp = await client.delete(f"{const.TASK_URL}/99999", headers=headers)
        assert resp.status_code == 404

    async def test_unauthorized_access(self, client):
        """测试未授权访问"""
        resp = await client.get(const.TASK_URL)
        assert resp.status_code == 401

        resp = await client.post(const.TASK_URL, json={
            "name": "test",
            "start_time": time.time(),
            "request_url": "http://example.com"
        })
        assert resp.status_code == 401

        resp = await client.get(f"{const.TASK_URL}/1")
        assert resp.status_code == 401

        resp = await client.delete(f"{const.TASK_URL}/1")
        assert resp.status_code == 401

    async def test_invalid_task_data(self, client, headers):
        """测试无效的任务数据"""
        resp = await client.post(const.TASK_URL, headers=headers, json={})
        assert resp.status_code == 422

        resp = await client.post(const.TASK_URL, headers=headers, json={
            "name": "invalid_method",
            "start_time": time.time(),
            "request_url": "http://example.com",
            "method": "INVALID_METHOD"
        })
        assert resp.status_code == 422

    async def test_user_isolation(self, client, headers, user):
        """测试用户任务隔离"""
        resp = await client.post(const.TASK_URL, headers=headers, json={
            "name": "user1_task",
            "start_time": time.time(),
            "request_url": "http://example.com/user1"
        })
        assert resp.status_code == 200
        task1_id = resp.json()["task_id"]

        user2_data = {"name": "user2", "password": "password", "email": "user2@test.com"}
        await client.post(const.USER_URL, json=user2_data)

        resp = await client.post(const.AUTH_TOKEN_URL, json={
            "name": "user2",
            "password": "password"
        })
        user2_headers = {"Authorization": f"Bearer {resp.json()['token']}"}

        resp = await client.get(f"{const.TASK_URL}/{task1_id}", headers=user2_headers)
        assert resp.status_code == 404

        await client.delete(f"{const.TASK_URL}/{task1_id}", headers=headers)


@pytest.mark.asyncio
class TestDramatiqActors:
    """测试Dramatiq Actors"""

    async def test_ping_actor_success(self, stub_broker, stub_worker): # 恢复fixture
        mock_task = AsyncMock(spec=RequestTask)
        mock_task.id = 1
        mock_task.request_url = "http://test.com/api"
        mock_task.method = "GET"
        mock_task.body = None
        mock_task.header = {}
        mock_task.callback_url = "http://callback.com/status"
        # Mock status and error_message fields as they are not in specs by default in AsyncMock
        mock_task.status = TaskStatus.PENDING
        mock_task.error_message = None

        with patch(
            'scheduler_service.models.RequestTask.get_or_none',
            AsyncMock(return_value=mock_task)
        ):
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.aread.return_value = b'{"status": "success"}'

            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_session.post.return_value = AsyncMock()

            with patch('scheduler_service.service.request.get_session', return_value=mock_session):
                from scheduler_service.service.request import ping
                ping.send(mock_task.id)

                # 等待任务完成
                stub_broker.join(queue_name=ping.queue_name)

                mock_session.get.assert_called_once_with(url=mock_task.request_url, headers={})
                mock_session.post.assert_called_once_with(
                    mock_task.callback_url,
                    json={
                        'response': '{"status": "success"}',
                        'code': 200,
                        'exception': None,
                        'status': RequestStatus.COMPLETE
                    }
                )
                # 验证状态流转
                assert mock_task.status == TaskStatus.COMPLETED
                assert mock_task.error_message is None
                assert mock_task.save.call_count >= 2 # Running + Completed

    async def test_ping_actor_http_error(self, stub_broker, stub_worker): # 恢复fixture
        mock_task = AsyncMock(spec=RequestTask)
        mock_task.id = 2
        mock_task.request_url = "http://nonexistent.com/api"
        mock_task.method = "GET"
        mock_task.body = None
        mock_task.header = {}
        mock_task.callback_url = "http://callback.com/status"
        mock_task.status = TaskStatus.PENDING
        mock_task.error_message = None

        with patch(
            'scheduler_service.models.RequestTask.get_or_none',
            AsyncMock(return_value=mock_task)
        ):
            mock_session = AsyncMock()
            mock_session.get.side_effect = httpx.RequestError(
                "Network error",
                request=httpx.Request("GET", mock_task.request_url)
            )
            mock_session.post.return_value = AsyncMock()

            with patch('scheduler_service.service.request.get_session', return_value=mock_session):
                from scheduler_service.service.request import ping
                ping.send(mock_task.id)

                # 等待任务完成
                stub_broker.join(queue_name=ping.queue_name)

                mock_session.get.assert_called_once_with(url=mock_task.request_url, headers={})
                mock_session.post.assert_called_once()
                args, kwargs = mock_session.post.call_args
                assert kwargs['json']['status'] == RequestStatus.FAIL
                assert 'Network error' in kwargs['json']['exception']
                
                # 验证状态流转
                assert mock_task.status == TaskStatus.FAILED
                assert "Network error" in str(mock_task.error_message)
                assert mock_task.save.call_count >= 2 # Running + Failed

    @pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH", "GET"])
    async def test_ping_actor_methods(self, method, stub_broker, stub_worker):
        """测试不同HTTP方法的ping actor"""
        mock_task = AsyncMock(spec=RequestTask)
        mock_task.id = 3
        mock_task.request_url = "http://test.com/api"
        mock_task.method = method
        mock_task.body = {"data": "test"} if method in ["POST", "PUT", "PATCH"] else None
        mock_task.header = {"Content-Type": "application/json"}
        mock_task.callback_url = "http://callback.com/status"

        with patch(
            'scheduler_service.models.RequestTask.get_or_none',
            AsyncMock(return_value=mock_task)
        ):
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.aread.return_value = b'{"status": "success"}'

            mock_session = AsyncMock()
            # 先设置默认的post返回值（用于回调）
            mock_session.post.return_value = AsyncMock()

            # 设置特定方法的返回值（如果是POST，这会覆盖上面的设置）
            mock_method = getattr(mock_session, method.lower())
            mock_method.return_value = mock_response

            with patch('scheduler_service.service.request.get_session', return_value=mock_session):
                from scheduler_service.service.request import ping
                ping.send(mock_task.id)

                stub_broker.join(queue_name=ping.queue_name)

                expected_kwargs = {
                    'url': mock_task.request_url,
                    'headers': mock_task.header
                }
                if mock_task.body:
                    expected_kwargs['json'] = mock_task.body

                # 对于POST方法，session.post会被调用两次（一次请求，一次回调）
                if method == "POST":
                    mock_method.assert_any_call(**expected_kwargs)
                else:
                    mock_method.assert_called_once_with(**expected_kwargs)

                # 验证回调
                # 注意：如果method是POST，mock_session.post已经被上面的逻辑验证过一部分了
                # 这里我们专门验证回调的那次调用
                mock_session.post.assert_called_with(
                    mock_task.callback_url,
                    json={
                        'response': '{"status": "success"}',
                        'code': 200,
                        'exception': None,
                        'status': RequestStatus.COMPLETE
                    }
                )
