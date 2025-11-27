import time
import pytest
from scheduler_service.models import RequestTask
from tests import const
from unittest.mock import MagicMock

@pytest.mark.asyncio
class TestTaskCron:
    """Test cron functionality for RequestTask"""

    async def test_create_task_with_cron(self, client, headers, user):
        """Test creating a task with a cron expression"""
        task_data = {
            "name": "cron_task",
            "start_time": time.time(),
            "request_url": "http://example.com",
            "callback_url": "http://example.com/callback",
            "method": "POST",
            "header": {"Content-Type": "application/json"},
            "body": {"key": "value"},
            "cron": "* * * * *"
        }

        resp = await client.post(const.TASK_URL, headers=headers, json=task_data)
        assert resp.status_code == 200
        response_data = resp.json()
        assert "task_id" in response_data

        task_id = response_data["task_id"]
        
        # Verify task in database
        task = await RequestTask.get(id=task_id)
        assert task.cron == "* * * * *"
        assert task.cron_count == 0
        assert task.job_id is not None # Verify job_id is generated
        assert task.message_id is None # No immediate Dramatiq message for cron tasks

        # Verify API response when getting the task
        resp = await client.get(f"{const.TASK_URL}/{task_id}", headers=headers)
        assert resp.status_code == 200
        task_details = resp.json()
        assert task_details["cron"] == "* * * * *"
        assert task_details["cron_count"] == 0
        assert task_details["job_id"] == task.job_id
        assert task_details["message_id"] is None

        # Verify job exists in scheduler
        from scheduler_service import get_scheduler
        scheduler = get_scheduler()
        job = scheduler.get_job(task.job_id)
        assert job is not None
        
        # Check trigger properties instead of exact string match to avoid timezone issues
        trigger_str = str(job.trigger)
        assert "cron[" in trigger_str
        assert "month='*'" in trigger_str
        assert "day='*'" in trigger_str
        assert "day_of_week='*'" in trigger_str
        assert "hour='*'" in trigger_str
        assert "minute='*'" in trigger_str

        # Delete task and verify job is removed
        resp = await client.delete(f"{const.TASK_URL}/{task_id}", headers=headers)
        assert resp.status_code == 200
        
        job = scheduler.get_job(task.job_id)
        assert job is None

    async def test_create_task_without_cron(self, client, headers, user, mocker):
        """Test creating a task without a cron expression (should trigger immediate Dramatiq task)"""
        # Mock dramatiq broker.send method
        mock_send = mocker.patch("scheduler_service.service.request.ping.send")
        mock_send.return_value = MagicMock(message_id="mock_message_id")

        task_data = {
            "name": "simple_task",
            "start_time": time.time(),
            "request_url": "http://example.com",
        }

        resp = await client.post(const.TASK_URL, headers=headers, json=task_data)
        assert resp.status_code == 200
        task_id = resp.json()["task_id"]

        task = await RequestTask.get(id=task_id)
        assert task.cron is None
        assert task.cron_count == 0
        assert task.job_id is None # Verify job_id is None
        assert task.message_id == "mock_message_id" # Verify immediate Dramatiq message

        resp = await client.get(f"{const.TASK_URL}/{task_id}", headers=headers)
        task_details = resp.json()
        assert task_details["cron"] is None
        assert task_details["job_id"] is None
        assert task_details["message_id"] == "mock_message_id"

        mock_send.assert_called_once_with(task.id)
        
        await task.delete()

    async def test_create_task_invalid_cron(self, client, headers, user):
        """Test creating a task with invalid cron expression"""
        task_data = {
            "name": "invalid_cron_task",
            "start_time": time.time(),
            "request_url": "http://example.com",
            "cron": "invalid * * *"
        }

        resp = await client.post(const.TASK_URL, headers=headers, json=task_data)
        assert resp.status_code == 400
        assert "Invalid cron expression" in resp.json()["detail"]
        
        # Verify task was not created (or deleted)
        tasks = await RequestTask.filter(name="invalid_cron_task")
        assert len(tasks) == 0
